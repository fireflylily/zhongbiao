-- 调整电信业务许可证的插入顺序
-- 先插入增值电信业务许可证，再插入基础电信业务许可证

-- 交换两个资质的 sort_order
UPDATE qualification_types
SET sort_order = 9
WHERE type_key = 'value_added_telecom_permit';

UPDATE qualification_types
SET sort_order = 10
WHERE type_key = 'basic_telecom_permit';

-- 验证修改
SELECT type_key, type_name, sort_order
FROM qualification_types
WHERE type_key IN ('value_added_telecom_permit', 'basic_telecom_permit')
ORDER BY sort_order;
