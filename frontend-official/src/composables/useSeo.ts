import { useHead } from '@unhead/vue'

interface SeoInput {
  title: string
  description?: string
  keywords?: string
  ogImage?: string
  // 6月24日新增：套餐页面可设置更精确的 SEO 提示
  pricing?: boolean
  pageType?: string
}

export function usePageSeo(seo: SeoInput) {
  // 6月24日新增：套餐页追加 structured data (JSON-LD)
  const ldJson: Record<string, any>[] = []
  if (seo.pricing) {
    ldJson.push({
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: '辰科MES',
      description: seo.description || '轻量化生产管理系统',
      brand: { '@type': 'Brand', name: '辰科MES' },
      offers: { '@type': 'Offer', category: 'SaaS' },
    })
  }

  useHead({
    title: seo.title,
    meta: [
      ...(seo.description ? [{ name: 'description', content: seo.description }] : []),
      ...(seo.keywords ? [{ name: 'keywords', content: seo.keywords }] : []),
      { property: 'og:title', content: seo.title },
      ...(seo.description ? [{ property: 'og:description', content: seo.description }] : []),
      ...(seo.ogImage ? [{ property: 'og:image', content: seo.ogImage }] : []),
      { property: 'og:type', content: seo.pageType || 'website' },
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: seo.title },
      ...(seo.description ? [{ name: 'twitter:description', content: seo.description }] : []),
    ],
    script: ldJson.length
      ? [
          {
            type: 'application/ld+json',
            innerHTML: JSON.stringify(ldJson[0]),
          },
        ]
      : [],
  })
}
