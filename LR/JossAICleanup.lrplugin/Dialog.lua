local LrBinding = import 'LrBinding'
local LrDialogs = import 'LrDialogs'
local LrFunctionContext = import 'LrFunctionContext'
local LrView = import 'LrView'
local bind = LrView.bind
local share = LrView.share

local PathUtil = require 'PathUtil'

local M = {}

function M.present()
    return LrFunctionContext.callWithContext('Joss AI Cleanup dialog', function(context)
        local f = LrView.osFactory()
        local props = LrBinding.makePropertyTable(context)
        props.provider = 'dashscope'
        props.operation = 'film_dust'
        props.quality = 'medium'
        props.model = ''
        props.prompt = ''
        props.corePath = PathUtil.defaultCorePath()
        props.outputFolder = PathUtil.defaultOutputFolder()
        props.rightsConfirmed = false

        local contents = f:column {
            bind_to_object = props,
            spacing = f:control_spacing(),

            f:static_text {
                title = '所选照片会先以 16 位 TIFF / ProPhoto RGB 渲染，再由本地 AI 核心处理。',
                fill_horizontal = 1,
                height_in_lines = 2,
            },

            f:row {
                f:static_text { title = 'AI 服务', width = share 'labelWidth' },
                f:popup_menu {
                    value = bind 'provider',
                    width = 230,
                    items = {
                        { title = '阿里百炼 / 万相', value = 'dashscope' },
                        { title = '火山方舟 / 豆包', value = 'volcengine' },
                        { title = '百度千帆', value = 'baidu' },
                        { title = 'Google Gemini', value = 'gemini' },
                        { title = 'OpenAI', value = 'openai' },
                        { title = 'OpenAI 兼容接口', value = 'custom-openai' },
                    },
                },
            },

            f:row {
                f:static_text { title = '处理类型', width = share 'labelWidth' },
                f:popup_menu {
                    value = bind 'operation',
                    width = 230,
                    items = {
                        { title = '胶片灰尘 / 毛发', value = 'film_dust' },
                        { title = '胶片划痕', value = 'film_scratch' },
                        { title = '智能降噪', value = 'denoise' },
                        { title = '清理画面干扰物（实验）', value = 'remove_object' },
                        { title = '授权覆盖物清理', value = 'authorized_overlay' },
                        { title = '自定义', value = 'custom' },
                    },
                },
            },

            f:row {
                f:static_text { title = '质量', width = share 'labelWidth' },
                f:popup_menu {
                    value = bind 'quality',
                    width = 230,
                    items = {
                        { title = '快速', value = 'low' },
                        { title = '标准', value = 'medium' },
                        { title = '精细', value = 'high' },
                    },
                },
            },

            f:row {
                f:static_text { title = '模型', width = share 'labelWidth' },
                f:edit_field {
                    value = bind 'model',
                    width_in_chars = 34,
                    tooltip = '留空使用本地核心为该服务设置的推荐模型。',
                },
            },

            f:row {
                f:static_text { title = '补充说明', width = share 'labelWidth' },
                f:edit_field {
                    value = bind 'prompt',
                    width_in_chars = 34,
                    height_in_lines = 3,
                },
            },

            f:row {
                f:static_text { title = '核心程序', width = share 'labelWidth' },
                f:edit_field { value = bind 'corePath', width_in_chars = 34 },
            },

            f:row {
                f:static_text { title = '输出目录', width = share 'labelWidth' },
                f:edit_field { value = bind 'outputFolder', width_in_chars = 34 },
            },

            f:checkbox {
                title = '我拥有图片或已获得移除文字、日期戳、Logo 等覆盖物的授权',
                value = bind 'rightsConfirmed',
            },

            f:static_text {
                title = '注意：Lightroom Classic 没有 Photoshop 式像素选区。本版本会处理整张渲染副本，适合胶片清洁和降噪；复杂物体移除建议在 Photoshop 中完成。',
                fill_horizontal = 1,
                height_in_lines = 4,
            },
        }

        local result = LrDialogs.presentModalDialog {
            title = 'Joss AI Cleanup',
            contents = contents,
            actionVerb = '开始处理',
            cancelVerb = '取消',
        }
        if result ~= 'ok' then
            return nil
        end
        return {
            provider = props.provider,
            operation = props.operation,
            quality = props.quality,
            model = props.model,
            prompt = props.prompt,
            corePath = props.corePath,
            outputFolder = props.outputFolder,
            rightsConfirmed = props.rightsConfirmed,
        }
    end)
end

return M
