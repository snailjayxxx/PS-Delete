local LrPathUtils = import 'LrPathUtils'
local LrFileUtils = import 'LrFileUtils'

local M = {}

function M.quote(value)
    value = tostring(value or '')
    if WIN_ENV then
        return '"' .. value:gsub('"', '\\"') .. '"'
    end
    return "'" .. value:gsub("'", "'\\''") .. "'"
end

function M.defaultCorePath()
    local appData = LrPathUtils.getStandardFilePath('appData')
    if WIN_ENV then
        return LrPathUtils.child(LrPathUtils.child(appData, 'Joss AI Cleanup'), 'joss-ai-cleanup-core.exe')
    end
    return LrPathUtils.child(LrPathUtils.child(appData, 'Joss AI Cleanup'), 'joss-ai-cleanup-core')
end

function M.defaultOutputFolder()
    local pictures = LrPathUtils.getStandardFilePath('pictures')
    return LrPathUtils.child(pictures, 'Joss AI Cleanup')
end

function M.ensureFolder(path)
    if not LrFileUtils.exists(path) then
        LrFileUtils.createAllDirectories(path)
    end
end

function M.outputPathForPhoto(photo, folder)
    local originalPath = photo:getRawMetadata('path')
    local leaf = LrPathUtils.leafName(originalPath)
    local base = LrPathUtils.removeExtension(leaf)
    local stamp = os.date('%Y%m%d-%H%M%S') .. '-' .. tostring(math.random(1000, 9999))
    return LrPathUtils.child(folder, base .. '_JossAI_' .. stamp .. '.tif')
end

return M
