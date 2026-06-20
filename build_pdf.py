# -*- coding: utf-8 -*-
"""生成 Offer捕手 方案说明 PDF（与 doc.html 内容同步，约 980 字）"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

FONT_CANDIDATES = [
    '/System/Library/Fonts/Supplemental/Songti.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]
FONT = next((p for p in FONT_CANDIDATES if os.path.exists(p)), FONT_CANDIDATES[0])
if FONT.endswith('.ttc'):
    pdfmetrics.registerFont(TTFont('Hei', FONT, subfontIndex=0))
    pdfmetrics.registerFont(TTFont('HeiB', FONT, subfontIndex=0))
else:
    pdfmetrics.registerFont(TTFont('Hei', FONT))
    pdfmetrics.registerFont(TTFont('HeiB', FONT))

TC, INK, GRAY, LINE = HexColor('#0052D9'), HexColor('#1a1a1a'), HexColor('#5a6068'), HexColor('#e6e9ee')
W, H = A4

title = ParagraphStyle('t', fontName='HeiB', fontSize=20, leading=27, textColor=INK)
sub   = ParagraphStyle('s', fontName='Hei', fontSize=10.5, leading=15, textColor=GRAY)
body  = ParagraphStyle('b', fontName='Hei', fontSize=10.2, leading=18, textColor=HexColor('#2b2f36'), spaceAfter=4, firstLineIndent=21)
lead  = ParagraphStyle('l', fontName='Hei', fontSize=10.2, leading=17, textColor=HexColor('#2b2f36'), backColor=HexColor('#f4f7fd'), leftIndent=8, rightIndent=8, spaceAfter=6)

class HeaderBar(Flowable):
    def __init__(self, w):
        Flowable.__init__(self)
        self.width, self.height = w, 4
    def draw(self):
        self.canv.setFillColor(TC); self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

class SectionNum(Flowable):
    def __init__(self, num, text, w=400):
        Flowable.__init__(self)
        self.num, self.text = num, text
        self.width, self.height = w, 22
    def draw(self):
        c = self.canv
        c.setFillColor(TC); c.roundRect(0, 0, 18, 18, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#ffffff')); c.setFont('HeiB', 10.5); c.drawCentredString(9, 5, str(self.num))
        c.setFillColor(TC); c.setFont('HeiB', 12.5); c.drawString(26, 4.5, self.text)

def hr():
    t = Table([['']], colWidths=[W - 50 * mm], rowHeights=[1])
    t.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1.2, TC)]))
    return t

doc = BaseDocTemplate('Offer捕手-方案说明文档.pdf', pagesize=A4,
                      leftMargin=25*mm, rightMargin=25*mm, topMargin=18*mm, bottomMargin=18*mm)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='n')

def footer(canvas, d):
    canvas.saveState()
    canvas.setFont('Hei', 8); canvas.setFillColor(HexColor('#9aa0a8'))
    canvas.drawString(d.leftMargin, 12*mm, 'Offer捕手 · 作业方案说明')
    canvas.drawRightString(W - d.rightMargin, 12*mm, '第 %d 页' % d.page)
    canvas.restoreState()

doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=footer)])

S = [HeaderBar(doc.width), Spacer(1, 10),
     Paragraph('「Offer捕手」学生求职匹配智能体', title), Spacer(1, 3),
     Paragraph('作业方案说明 ｜ 腾讯 AI-HR 线上实战营（全文约 980 字）', sub),
     Spacer(1, 8), hr(), Spacer(1, 10),
     Paragraph('<b>Demo：</b>https://sjy18383566607.github.io/tencent-offer-catcher/index.html', lead)]

sections = [
    ('一', '问题诊断', '学生求职有三类痛点：<b>岗位难筛</b>——腾讯校招社招合计三千余岗，人工比对 JD 成本高；<b>匹配度不明</b>——简历是否契合岗位缺乏量化；<b>优化无方向</b>——不清楚岗位关键词，简历易空泛。落地中还发现：青云计划岗位 API 用 topicDetail 字段，旧爬虫致 258 条职责为空；技术岗一次匹配千余条，全量渲染致白屏；渲染函数缺方法，出现「有推荐无卡片」。'),
    ('二', '方案设计', '「Offer捕手」构建「录入—匹配—诊断」闭环。<b>数据层</b>：Python 爬取 join.qq.com 与 careers.tencent.com 官方接口，库内 3042 条真岗位。<b>录入</b>：简历粘贴+表单，技能标签与进度条生成能力画像。<b>匹配</b>：按城市、类型、校社招、人才专项过滤后，对技能/地点/类别/学历/JD 关键词加权打分，首屏展示 10 条、点击「加载更多」追加。<b>诊断</b>：针对目标岗输出评分、差距与润色建议，支持导出。'),
    ('三', 'AI 工具选型理由', '<b>Cursor</b>：AI 辅助编码，快速完成联调与修 bug，适合单人全栈交付。<b>规则引擎匹配</b>：不用黑盒 LLM 打分，结果可复现、无 API 费用，亮点标签可对照 JD 原文，便于答辩演示。<b>Python 爬虫</b>：批量拉取与回填官网字段，保证数据真实。<b>GitHub Pages</b>：静态部署，推送即发布，满足公网访问要求。'),
    ('四', '关键配置', '岗位库 tencent_jobs.json（校招 534+社招 2508）；爬虫 scrape_tencent_jobs.py，补全脚本映射青云计划 topicDetail→职责；匹配分项计分总分封顶 98；筛选项含青云计划-应届生/实习生等人才专项；分页常量 DISPLAY_PAGE_SIZE=10；线上地址 sjy18383566607.github.io/tencent-offer-catcher/。'),
    ('五', '迭代记录与效果评估', '<b>迭代</b>：①原型四模块 → ②接入真数据 → ③回填 250 条空 JD → ④改分页解决白屏 → ⑤修复渲染错误。<b>效果</b>：匹配千级岗位数秒完成，首屏秒开；详情职责覆盖率约 99%（除 8 条已下架）；诊断给出可执行优化话术。整体将找岗、比岗、改简历整合为数据驱动流程。'),
]

for n, t, content in sections:
    S += [SectionNum(n, t, doc.width), Spacer(1, 7), Paragraph(content, body), Spacer(1, 6)]

S.append(Paragraph('<b>交付物</b>：Demo 见上文链接；PDF 文件 Offer捕手-方案说明文档.pdf', lead))
doc.build(S)
print('PDF built: Offer捕手-方案说明文档.pdf')
