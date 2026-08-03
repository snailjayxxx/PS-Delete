local LrApplication = import 'LrApplication'
local LrDialogs = import 'LrDialogs'
local LrExportSession = import 'LrExportSession'
local LrFileUtils = import 'LrFileUtils'
local LrPathUtils = import 'LrPathUtils'
local LrProgressScope = import 'LrProgressScope'
local LrTasks = import 'LrTasks'

local Core = require 'Core'
local Dialog = require 'Dialog'
local PathUtil = require 'PathUtil'

LrTasks.startAsyncTask(function()
    local catalog = LrApplication.activeCatalog()
    local photos = catalog:getTargetPhotos()
    if not photos or #photos == 0 then
        LrDialogs.message('Joss AI Cleanup', '请先选择至少一张照片。', 'warning')
        return
    end

    local settings = Dialog.present()
    if not settings then return end
    if settings.operation == 'authorized_overlay' and not settings.rightsConfirmed then
        LrDialogs.message('Joss AI Cleanup', '授权覆盖物清理必须先确认图片处理权。', 'warning')
        return
    end

    PathUtil.ensureFolder(settings.outputFolder)
    local tempFolder = LrPathUtils.getStandardFilePath('temp')
    local renderFolder = LrPathUtils.child(tempFolder, 'JossAICleanup-LR')
    PathUtil.ensureFolder(renderFolder)

    local exportSettings = {
        LR_export_destinationType = 'specificFolder',
        LR_export_destinationPathPrefix = renderFolder,
        LR_export_useSubfolder = false,
        LR_collisionHandling = 'overwrite',
        LR_format = 'TIFF',
        LR_tiff_bitDepth = 16,
        LR_tiff_compressionMethod = 'compressionMethod_ZIP',
        LR_colorSpace = 'ProPhotoRGB',
        LR_export_postProcessing = 'doNothing',
        LR_useWatermark = false,
        LR_includeVideoFiles = false,
        LR_renamingTokensOn = true,
        LR_tokens = '{{image_name}}-JossAI-source',
    }

    local exportSession = LrExportSession {
        photosToExport = photos,
        exportSettings = exportSettings,
    }

    local progress = LrProgressScope {
        title = 'Joss AI Cleanup 正在处理',
        caption = '准备渲染照片……',
    }

    local completed = 0
    local failed = {}
    local total = #photos

    for rendition, photo in exportSession:renditions { stopIfCanceled = true } do
        if progress:isCanceled() then break end
        progress:setPortionComplete(completed, total)
        progress:setCaption('正在渲染：' .. tostring(photo:getFormattedMetadata('fileName')))

        local success, renderedPath = rendition:waitForRender()
        if not success then
            table.insert(failed, tostring(renderedPath))
        else
            local outputPath = PathUtil.outputPathForPhoto(photo, settings.outputFolder)
            progress:setCaption('AI 正在处理：' .. tostring(photo:getFormattedMetadata('fileName')))
            local ok, err = Core.run(settings, renderedPath, outputPath)
            if ok then
                local importOk, importErr = pcall(function()
                    catalog:withWriteAccessDo('导入 Joss AI 结果', function()
                        local newPhoto = catalog:addPhoto(outputPath, photo, 'above')
                        local keyword = catalog:createKeyword('Joss AI Cleanup', {}, true, nil, true)
                        if keyword and newPhoto then newPhoto:addKeyword(keyword) end
                    end)
                end)
                if not importOk then
                    table.insert(failed, tostring(importErr))
                end
            else
                table.insert(failed, tostring(err))
            end
            pcall(function() LrFileUtils.delete(renderedPath) end)
        end
        completed = completed + 1
    end

    progress:setPortionComplete(1, 1)
    progress:done()

    if #failed == 0 then
        LrDialogs.message('Joss AI Cleanup', '处理完成，共导入 ' .. tostring(completed) .. ' 张 AI 结果。', 'info')
    else
        LrDialogs.message(
            'Joss AI Cleanup',
            '已完成 ' .. tostring(completed) .. ' 张，其中 ' .. tostring(#failed) .. ' 张失败。\n\n' .. table.concat(failed, '\n'),
            'warning'
        )
    end
end)
