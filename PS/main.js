const photoshop = require("photoshop");
const { app, imaging, core } = photoshop;

const CORE_URL = "http://127.0.0.1:18780";
const $ = (id) => document.getElementById(id);

function setMessage(text, type = "") {
  const el = $("message");
  el.textContent = text;
  el.className = `message ${type}`.trim();
}

function toNumber(value) {
  if (typeof value === "number") return value;
  if (value && typeof value.value === "number") return value.value;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error("无法读取选区坐标");
  return parsed;
}

function bytesToBase64(bytes) {
  const chunk = 0x8000;
  let binary = "";
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, Math.min(i + chunk, bytes.length)));
  }
  return btoa(binary);
}

function base64ToBytes(value) {
  const binary = atob(value);
  const result = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) result[i] = binary.charCodeAt(i);
  return result;
}

function normalizeRgb(data, components, width, height) {
  if (components === 3) return data;
  const rgb = new Uint8Array(width * height * 3);
  for (let src = 0, dst = 0; dst < rgb.length; src += components, dst += 3) {
    rgb[dst] = data[src];
    rgb[dst + 1] = data[src + 1] ?? data[src];
    rgb[dst + 2] = data[src + 2] ?? data[src];
  }
  return rgb;
}

function normalizeMask(data, components, width, height) {
  if (components === 1) return data;
  const mask = new Uint8Array(width * height);
  for (let src = 0, dst = 0; dst < mask.length; src += components, dst += 1) {
    mask[dst] = data[src];
  }
  return mask;
}

async function request(path, options = {}) {
  const response = await fetch(`${CORE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let body = null;
  try { body = await response.json(); } catch (_) { body = null; }
  if (!response.ok) {
    const detail = body?.detail || body?.message || `${response.status} ${response.statusText}`;
    throw new Error(detail);
  }
  return body;
}

async function checkCore() {
  try {
    const health = await request("/health");
    $("coreStatus").textContent = `核心在线 ${health.version}`;
    $("coreStatus").className = "status online";
    await updateProviderStatus();
    return true;
  } catch (error) {
    $("coreStatus").textContent = "核心未连接";
    $("coreStatus").className = "status offline";
    $("providerStatus").textContent = "请先安装并启动 Joss AI Cleanup Core。";
    return false;
  }
}

async function updateProviderStatus() {
  try {
    const data = await request("/v1/providers");
    const provider = $("provider").value;
    const status = data.providers?.[provider];
    if (!status) return;
    $("providerStatus").textContent = status.configured
      ? `已配置。当前模型：${status.model || status.default_model}`
      : `尚未配置 API Key。推荐模型：${status.default_model}`;
    if (!$("model").value) $("model").placeholder = status.default_model || "留空使用推荐模型";
  } catch (_) {
    // Core status area already communicates connection errors.
  }
}

async function saveProvider() {
  const provider = $("provider").value;
  const payload = {
    api_key: $("apiKey").value || null,
    model: $("model").value || null,
    base_url: $("baseUrl").value || null,
    workspace_id: $("workspaceId").value || null,
  };
  await request(`/v1/providers/${provider}`, { method: "PUT", body: JSON.stringify(payload) });
  $("apiKey").value = "";
  await updateProviderStatus();
  setMessage("API 设置已保存在本机。", "success");
}

function expandedBounds(doc, selectionBounds, percent) {
  const left = toNumber(selectionBounds.left);
  const top = toNumber(selectionBounds.top);
  const right = toNumber(selectionBounds.right);
  const bottom = toNumber(selectionBounds.bottom);
  const width = Math.max(1, right - left);
  const height = Math.max(1, bottom - top);
  const padX = Math.round(width * percent / 100);
  const padY = Math.round(height * percent / 100);
  return {
    left: Math.max(0, Math.floor(left - padX)),
    top: Math.max(0, Math.floor(top - padY)),
    right: Math.min(toNumber(doc.width), Math.ceil(right + padX)),
    bottom: Math.min(toNumber(doc.height), Math.ceil(bottom + padY)),
  };
}

async function collectSelectionPayload() {
  const doc = app.activeDocument;
  if (!doc) throw new Error("请先打开一张图片。");
  const selectionBounds = doc.selection.bounds;
  if (!selectionBounds) throw new Error("请先用套索、对象选择或其他工具建立选区。");

  const bounds = expandedBounds(doc, selectionBounds, Number($("context").value));
  const width = bounds.right - bounds.left;
  const height = bounds.bottom - bounds.top;
  if (width * height > 40000000) throw new Error("选区及上下文超过 4000 万像素，请缩小选区或上下文。");

  const pixelResult = await imaging.getPixels({
    documentID: doc.id,
    sourceBounds: bounds,
    targetSize: { width, height },
    colorSpace: "RGB",
    colorProfile: "sRGB IEC61966-2.1",
    componentSize: 8,
    applyAlpha: true,
  });
  const selectionResult = await imaging.getSelection({
    documentID: doc.id,
    sourceBounds: bounds,
    targetSize: { width, height },
  });

  try {
    const pixelData = await pixelResult.imageData.getData({ chunky: true });
    const maskData = await selectionResult.imageData.getData({ chunky: true });
    const actualWidth = pixelResult.imageData.width;
    const actualHeight = pixelResult.imageData.height;
    if (selectionResult.imageData.width !== actualWidth || selectionResult.imageData.height !== actualHeight) {
      throw new Error("Photoshop 返回的图像与选区蒙版尺寸不一致。");
    }
    return {
      doc,
      bounds,
      width: actualWidth,
      height: actualHeight,
      image_rgb_b64: bytesToBase64(normalizeRgb(pixelData, pixelResult.imageData.components, actualWidth, actualHeight)),
      mask_l_b64: bytesToBase64(normalizeMask(maskData, selectionResult.imageData.components, actualWidth, actualHeight)),
    };
  } finally {
    pixelResult.imageData.dispose();
    selectionResult.imageData.dispose();
  }
}

async function applyResult(payload, response) {
  if (response.width !== payload.width || response.height !== payload.height || response.components !== 4) {
    throw new Error("本地核心返回了不兼容的图像尺寸或通道数。");
  }
  const rgba = base64ToBytes(response.image_rgba_b64);
  const expected = response.width * response.height * 4;
  if (rgba.length !== expected) throw new Error("返回图像数据长度不正确。");

  await core.executeAsModal(async () => {
    const imageData = await imaging.createImageDataFromBuffer(rgba, {
      width: response.width,
      height: response.height,
      components: 4,
      chunky: true,
      colorSpace: "RGB",
      colorProfile: "sRGB IEC61966-2.1",
    });
    try {
      const layer = await payload.doc.createLayer({
        name: `Joss AI - ${response.provider} - ${new Date().toLocaleTimeString()}`,
      });
      await imaging.putPixels({
        documentID: payload.doc.id,
        layerID: layer.id,
        imageData,
        replace: true,
        targetBounds: { left: payload.bounds.left, top: payload.bounds.top },
        commandName: "Joss AI Cleanup",
      });
    } finally {
      imageData.dispose();
    }
  }, { commandName: "Joss AI Cleanup" });
}

async function runEdit() {
  const button = $("runButton");
  button.disabled = true;
  setMessage("正在读取 Photoshop 选区……");
  try {
    const operation = $("operation").value;
    if (operation === "authorized_overlay" && !$("rightsConfirmed").checked) {
      throw new Error("请先确认你拥有该图片或已获得处理授权。");
    }
    if (!(await checkCore())) throw new Error("本地处理核心未启动。");
    const payload = await collectSelectionPayload();
    setMessage(`正在调用 ${$("provider").selectedOptions[0].textContent}，请不要关闭文档……`);
    const response = await request("/v1/edit/raw", {
      method: "POST",
      body: JSON.stringify({
        provider: $("provider").value,
        model: $("model").value || null,
        operation,
        prompt: $("prompt").value,
        width: payload.width,
        height: payload.height,
        image_rgb_b64: payload.image_rgb_b64,
        mask_l_b64: payload.mask_l_b64,
        quality: $("quality").value,
        rights_confirmed: $("rightsConfirmed").checked,
      }),
    });
    setMessage("正在写入新的 Photoshop 图层……");
    await applyResult(payload, response);
    setMessage(`处理完成：${response.provider} / ${response.model}`, "success");
  } catch (error) {
    console.error(error);
    setMessage(error?.message || String(error), "error");
  } finally {
    button.disabled = false;
  }
}

$("context").addEventListener("input", () => {
  $("contextValue").textContent = `${$("context").value}%`;
});
$("operation").addEventListener("change", () => {
  $("rightsRow").classList.toggle("hidden", $("operation").value !== "authorized_overlay");
});
$("provider").addEventListener("change", updateProviderStatus);
$("runButton").addEventListener("click", runEdit);
$("refreshButton").addEventListener("click", checkCore);
$("saveProviderButton").addEventListener("click", async () => {
  try { await saveProvider(); } catch (error) { setMessage(error.message || String(error), "error"); }
});

checkCore();
