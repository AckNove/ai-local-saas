import { get, post, patch } from './client'
import client from './client'
import type { PageResult, Package, PackageInput } from '../types'

// 团购套餐接口封装。

export function listPackages(params?: {
  merchant_id?: number
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}): Promise<PageResult<Package>> {
  return get<PageResult<Package>>('/catalog/packages', params)
}

export function createPackage(body: PackageInput): Promise<Package> {
  return post<Package>('/catalog/packages', body)
}

export function updatePackage(id: number, body: Partial<PackageInput>): Promise<Package> {
  return patch<Package>(`/catalog/packages/${id}`, body)
}

export function publishPackage(id: number): Promise<Package> {
  return post<Package>(`/catalog/packages/${id}/publish`)
}

export function offShelfPackage(id: number): Promise<Package> {
  return post<Package>(`/catalog/packages/${id}/off-shelf`)
}

/** 上传单张图片，返回可访问 URL（同源 /uploads/xxx）。 */
export async function uploadImage(file: File): Promise<string> {
  const fd = new FormData()
  fd.append('file', file)
  const r = await client.post('/upload/image', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  const body = r.data
  if (body && body.code === 0) return body.data.url as string
  throw new Error(body?.message || '上传失败')
}
