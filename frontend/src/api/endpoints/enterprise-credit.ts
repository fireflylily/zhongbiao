/**
 * 企业征信API端点
 *
 * 集成第三方企业征信API，提供企业信息查询和自动填充功能
 */

import { apiClient } from '../client'
import type { ApiResponse } from '@/types'

/**
 * 企业搜索结果
 */
export interface EnterpriseSearchResult {
  company_ss_id: string  // 企业ID（足迹ID）
  company_name: string   // 企业名称
  usc_code: string       // 统一社会信用代码
}

/**
 * 企业详细信息
 */
export interface EnterpriseDetail {
  company_ss_id: string           // 企业ID
  company_name: string            // 企业名称
  former_name?: string            // 曾用名
  short_name?: string             // 简称
  usc_code: string                // 统一社会信用代码
  reg_no?: string                 // 注册号
  legal_person: string            // 法定代表人
  reg_addr: string                // 注册地址
  reg_province_code?: string      // 注册省份编码
  reg_province?: string           // 注册省份
  reg_city_code?: string          // 注册城市编码
  reg_city?: string               // 注册城市
  reg_district_code?: string      // 注册区/县编码
  reg_district?: string           // 注册区/县
  reg_gov?: string                // 登记机关
  reg_capital: string             // 注册资本（金额+币种）
  reg_capital_amt?: number        // 注册资本金额（万元）
  paid_capital_amt?: number       // 实缴资本金额（万元）
  est_date: string                // 成立日期
  start_date?: string             // 营业期限开始日期
  end_date?: string               // 营业期限终止日期
  cancel_date?: string            // 注销日期
  revoke_date?: string            // 吊销日期
  approved_date?: string          // 核准日期
  business_type: string           // 公司类型
  business_type_code?: string     // 公司类型编码
  business_scope: string          // 经营范围
  company_status?: string         // 经营状态
  industry_code?: string          // 行业代码
  industry_section?: string       // 行业门类
  industry_division?: string      // 行业大类
  industry_group?: string         // 行业中类
  industry_class?: string         // 行业小类
  email?: string                  // 企业电子邮箱
  website?: string                // 企业网址
  tel: string                     // 企业电话
  employee_num?: string           // 职工人数
  tax_type?: string               // 税种
  capital_type_code?: string      // 经济类型编码
  capital_type?: string           // 经济类型
  shareholder?: Array<{           // 股东信息
    shareholder_name?: string
    shareholder_ss_id?: number
    shareholder_ratio?: number
    subscribed_capital_amt?: number
    subscribed_date?: string
    subscribed_type?: string
    paid_capital_amt?: number
    paid_date?: string
    paid_type?: string
  }>
  manager?: Array<{               // 管理人员信息
    person_name?: string
    position?: string
    education?: string
    shareholder_ratio?: number
  }>
}

/**
 * 企业征信API
 */
export const enterpriseCreditApi = {
  /**
   * 搜索企业列表
   *
   * @param keyword 企业名称或统一社会信用代码
   * @returns 企业列表
   */
  async searchEnterprises(keyword: string): Promise<ApiResponse<EnterpriseSearchResult[]>> {
    return apiClient.post('/enterprise/search', { keyword })
  },

  /**
   * 获取企业详细信息
   *
   * @param companySsId 企业ID（足迹ID）
   * @returns 企业详细信息
   */
  async getEnterpriseDetail(companySsId: string): Promise<ApiResponse<EnterpriseDetail>> {
    return apiClient.get(`/enterprise/detail/${companySsId}`)
  }
}
