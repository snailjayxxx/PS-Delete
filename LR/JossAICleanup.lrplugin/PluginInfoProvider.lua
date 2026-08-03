local LrView = import 'LrView'
local bind = LrView.bind

return {
    sectionsForTopOfDialog = function(f, propertyTable)
        return {
            {
                title = 'Joss AI Cleanup 0.1.0',
                f:column {
                    spacing = f:control_spacing(),
                    f:static_text {
                        title = '本插件将 Lightroom Classic 的渲染副本交给本地处理核心，再自动导回目录。',
                        fill_horizontal = 1,
                        height_in_lines = 2,
                    },
                    f:static_text {
                        title = 'API Key 由 Joss AI Cleanup Core 保存在本机系统凭据库中。',
                        fill_horizontal = 1,
                        height_in_lines = 2,
                    },
                },
            },
        }
    end,
}
