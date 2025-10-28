-- Migration: Update qualification_types table to use new 4-credit-qualification structure
-- Date: 2025-10-28
-- Description: Updates qualification_types table to match the new 4-qualification structure
--
-- Changes:
-- 1. Remove old credit qualification types: credit_china_check, gov_procurement_check
-- 2. Keep tax_violation_check (already exists)
-- 3. Add 3 new credit qualification types: dishonest_executor, gov_procurement_creditchina, gov_procurement_ccgp

-- Step 1: Backup the old data (create a backup record)
-- Note: qualification_types is a reference table, not transactional data, so we just log the change

-- Step 2: Delete old qualification types that are no longer used
DELETE FROM qualification_types WHERE type_key IN ('credit_china_check', 'gov_procurement_check');

-- Step 3: Update tax_violation_check name (optional - for consistency)
UPDATE qualification_types
SET type_name = '重大税收违法案件当事人名单（信用中国）'
WHERE type_key = 'tax_violation_check';

-- Step 4: Insert new qualification types
-- Note: Using INSERT OR IGNORE to avoid errors if they already exist
INSERT OR IGNORE INTO qualification_types (type_key, type_name, category, is_required, allow_multiple_files, version_label, sort_order) VALUES
    ('dishonest_executor', '失信被执行人名单（信用中国）', '信用证明', FALSE, FALSE, NULL, 20),
    ('gov_procurement_creditchina', '政府采购严重违法失信（信用中国）', '信用证明', FALSE, FALSE, NULL, 22),
    ('gov_procurement_ccgp', '政府采购严重违法失信行为信息记录（政府采购网）', '信用证明', FALSE, FALSE, NULL, 23);

-- Step 5: Verify the migration
-- Expected: 4 credit qualification types
-- SELECT type_key, type_name, category, sort_order
-- FROM qualification_types
-- WHERE category = '信用证明'
-- ORDER BY sort_order;

-- Step 6: Check if any old keys remain (should return 0 rows)
-- SELECT type_key FROM qualification_types WHERE type_key IN ('credit_china_check', 'gov_procurement_check');
