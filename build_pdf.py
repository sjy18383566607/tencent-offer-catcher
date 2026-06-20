# -*- coding: utf-8 -*-
"""生成 Offer捕手 方案说明 PDF（与 doc.html 内容同步）"""
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

TC, INK, GRAY = HexColor('#0052D9'), HexColor('#1a1a1a'), HexColor('#5a6068')
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
     Paragraph('作业方案说明 ｜ 腾讯 AI-HR 线上实战营（全文约 990 字）', sub),
     Spacer(1, 8), hr(), Spacer(1, 10),
     Paragraph('<b>公网 Demo：</b>https://sjy18383566607.github.io/tencent-offer-catcher/index.html', lead)]

sections = [
    ('一', '问题诊断',
     '腾讯校招/实习场景下，学生求职面临<b>信息过载</b>（三千余岗难以及时筛选）、<b>匹配不可见</b>（简历契合度缺乏量化）、<b>优化缺抓手</b>（不清楚岗位关键词）三大痛点。本项目直击上述需求，打造可公网访问、可完整演示的求职匹配智能体，帮助学生从盲目海投转向精准投递。'),
    ('二', '方案设计',
     '「Offer捕手」构建「录入—匹配—诊断」闭环。<b>数据层</b>：Python 爬虫直连腾讯校招与社招官方接口，沉淀 3042 条真岗位。<b>录入</b>：简历粘贴+表单双通道，技能标签与进度条生成能力画像。<b>匹配</b>：支持城市、类型、校社招、青云计划等专项筛选，六维加权打分并输出可解释亮点。<b>诊断</b>：针对目标岗给出评分、差距与润色话术，支持导出。'),
    ('三', 'AI 工具选型理由',
     '<b>Cursor</b>：AI 辅助全栈开发，高效完成需求拆解与联调，保障单人高质量交付。<b>规则引擎匹配</b>：多维加权、结果可复现，亮点可对照 JD 原文，答辩演示清晰可信。<b>Python 自动化</b>：批量采集与字段映射，数据权威真实。<b>GitHub Pages</b>：静态部署、推送即上线，零运维满足公网交付。'),
    ('四', '关键配置',
     '岗位库校招 534+社招 2508 条；青云计划字段 topicDetail 智能映射；匹配最高 98 分；人才专项与校社招联动筛选；分页 DISPLAY_PAGE_SIZE=10；线上 sjy18383566607.github.io/tencent-offer-catcher/。'),
    ('五', '迭代记录与效果评估',
     '经历五轮迭代，持续放大产品价值：①四模块原型闭环；②接入官方真数据；③<b>数据治理</b>——识别青云计划专属结构，自动回填 250 条官网原文，详情覆盖率达 99%；④<b>体验升级</b>——全量匹配+「首屏 10 条/加载更多」，千级结果秒开；⑤<b>交互精修</b>——筛选联动、亮点可视化、详情完善。最终实现数秒完成全库匹配，帮助学生数据驱动选岗、定向优化简历，达到可参赛、可答辩水准。'),
]

for n, t, content in sections:
    S += [SectionNum(n, t, doc.width), Spacer(1, 7), Paragraph(content, body), Spacer(1, 6)]

S.append(Paragraph('<b>交付物</b>：Demo 与 PDF 均已发布至 GitHub Pages，链接见 doc.html', lead))
doc.build(S)
print('PDF built: Offer捕手-方案说明文档.pdf')
