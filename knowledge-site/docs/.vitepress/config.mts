import { defineConfig } from 'vitepress'
import { readdirSync, statSync, existsSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'

// 定位源码目录（兼容 .vitepress 在 docs 内/外的两种布局）
const CWD = process.cwd()
const SRC = existsSync(join(CWD, 'docs')) ? join(CWD, 'docs') : CWD

// 根据真实目录结构自动生成侧边栏
function scanSidebar(relDir) {
  const rootDir = join(SRC, relDir)
  const items = []
  if (!existsSync(rootDir)) return items
  for (const name of readdirSync(rootDir).sort()) {
    const full = join(rootDir, name)
    if (statSync(full).isDirectory()) {
      const subs = []
      for (const sub of readdirSync(full).sort()) {
        if (sub.toLowerCase().endsWith('.md')) {
          subs.push({ text: sub.replace(/\.md$/, ''), link: `/${relative(SRC, join(full, sub)).replace(/\\/g, '/')}` })
        }
      }
      items.push({ text: name, collapsed: false, items: subs.length ? subs : [] })
    } else if (name.toLowerCase().endsWith('.md') && name !== 'index.md') {
      items.push({ text: name.replace(/\.md$/, ''), link: `/${relative(SRC, join(full, name)).replace(/\\/g, '/')}` })
    } else if (name === 'index.md') {
      items.push({ text: '概览', link: `/${relative(SRC, join(full, name)).replace(/\\/g, '/')}` })
    }
  }
  return items
}

export default defineConfig({
  title: 'CenkorMES 知识库',
  description: '多项目统一知识库 · VitePress',
  base: '/',
  lang: 'zh-CN',
  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,
  markdown: {
    lineNumbers: true
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: 'LightMes/CenkorMES', link: '/lightmes/' },
      { text: '个人学习', link: '/personal/' }
    ],
    sidebar: {
      '/lightmes/': scanSidebar('lightmes'),
      '/personal/': scanSidebar('personal'),
      '/': [
        { text: '项目导航', items: [
          { text: 'LightMes/CenkorMES', link: '/lightmes/' },
          { text: '个人学习', link: '/personal/' }
        ] }
      ]
    },
    search: { provider: 'local' },
    outline: { level: [2, 3] },
    footer: { message: 'CenkorMES 多项目知识库', copyright: '' }
  }
})