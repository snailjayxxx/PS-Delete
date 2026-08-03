local LrFileUtils = import 'LrFileUtils'
local LrTasks = import 'LrTasks'

local PathUtil = require 'PathUtil'

local M = {}

function M.run(settings, inputPath, outputPath)
    if not LrFileUtils.exists(settings.corePath) then
        return false, '找不到本地核心程序：' .. tostring(settings.corePath)
    end

    local command = table.concat({
        PathUtil.quote(settings.corePath),
        'edit-file',
        '--input', PathUtil.quote(inputPath),
        '--output', PathUtil.quote(outputPath),
        '--provider', PathUtil.quote(settings.provider),
        '--operation', PathUtil.quote(settings.operation),
        '--quality', PathUtil.quote(settings.quality),
        '--prompt', PathUtil.quote(settings.prompt or ''),
    }, ' ')

    if settings.model and settings.model ~= '' then
        command = command .. ' --model ' .. PathUtil.quote(settings.model)
    end
    if settings.rightsConfirmed then
        command = command .. ' --rights-confirmed'
    end

    local exitCode = LrTasks.execute(command)
    if exitCode ~= 0 then
        return false, '本地核心处理失败，退出码：' .. tostring(exitCode)
    end
    if not LrFileUtils.exists(outputPath) then
        return false, '本地核心未生成输出文件。'
    end
    return true, nil
end

return M
