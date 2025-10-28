-- Migration: Update credit qualification keys to new 4-qualification structure
-- Date: 2025-10-28
-- Description: Migrates old credit qualification keys to the new standardized keys
--
-- Old keys → New keys mapping:
-- credit_dishonest → dishonest_executor (失信被执行人名单)
-- credit_corruption (with "税收" in filename) → tax_violation_check (重大税收违法案件当事人名单)
-- credit_corruption (with "失信" in filename) → gov_procurement_creditchina (信用中国-政府采购严重违法失信)
-- credit_tax → gov_procurement_creditchina (信用中国-政府采购严重违法失信)
-- credit_procurement → gov_procurement_ccgp (政府采购网-政府采购严重违法失信行为信息记录)

-- Step 1: Backup the old data (create a backup table)
CREATE TABLE IF NOT EXISTS company_qualifications_backup_20251028 AS
SELECT * FROM company_qualifications
WHERE qualification_key IN ('credit_dishonest', 'credit_corruption', 'credit_tax', 'credit_procurement');

-- Step 2: Update credit_dishonest → dishonest_executor
UPDATE company_qualifications
SET
    qualification_key = 'dishonest_executor',
    qualification_name = '失信被执行人名单（信用中国）',
    updated_at = CURRENT_TIMESTAMP
WHERE qualification_key = 'credit_dishonest';

-- Step 3: Update credit_corruption → tax_violation_check (if filename contains "税收")
UPDATE company_qualifications
SET
    qualification_key = 'tax_violation_check',
    qualification_name = '重大税收违法案件当事人名单（信用中国）',
    updated_at = CURRENT_TIMESTAMP
WHERE qualification_key = 'credit_corruption'
AND (original_filename LIKE '%税收%' OR original_filename LIKE '%tax%');

-- Step 4: Update remaining credit_corruption → gov_procurement_creditchina
UPDATE company_qualifications
SET
    qualification_key = 'gov_procurement_creditchina',
    qualification_name = '政府采购严重违法失信（信用中国）',
    updated_at = CURRENT_TIMESTAMP
WHERE qualification_key = 'credit_corruption';

-- Step 5: Update credit_tax → gov_procurement_creditchina
-- First, find the max file_sequence for each company_id
-- Then update with file_sequence = max + 1 to avoid conflicts
UPDATE company_qualifications
SET
    qualification_key = 'gov_procurement_creditchina',
    qualification_name = '政府采购严重违法失信（信用中国）',
    file_sequence = (
        SELECT COALESCE(MAX(file_sequence), 0) + 1
        FROM company_qualifications AS cq2
        WHERE cq2.company_id = company_qualifications.company_id
        AND cq2.qualification_key = 'gov_procurement_creditchina'
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE qualification_key = 'credit_tax';

-- Step 6: Update credit_procurement → gov_procurement_ccgp
UPDATE company_qualifications
SET
    qualification_key = 'gov_procurement_ccgp',
    qualification_name = '政府采购严重违法失信行为信息记录（政府采购网）',
    updated_at = CURRENT_TIMESTAMP
WHERE qualification_key = 'credit_procurement';

-- Step 7: Verify the migration
-- SELECT qualification_key, COUNT(*) as count, GROUP_CONCAT(original_filename, '; ') as filenames
-- FROM company_qualifications
-- WHERE qualification_key IN ('dishonest_executor', 'tax_violation_check', 'gov_procurement_creditchina', 'gov_procurement_ccgp')
-- GROUP BY qualification_key;

-- Step 8: Check if any old keys remain (should return 0 rows)
-- SELECT qualification_key, COUNT(*) as count
-- FROM company_qualifications
-- WHERE qualification_key IN ('credit_dishonest', 'credit_corruption', 'credit_tax', 'credit_procurement')
-- GROUP BY qualification_key;
