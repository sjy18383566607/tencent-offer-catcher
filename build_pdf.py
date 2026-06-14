# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# —— 注册思源黑体（Noto Sans CJK SC） ——
pdfmetrics.registerFont(TTFont('Hei',  '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', subfontIndex=3))
pdfmetrics.registerFont(TTFont('HeiB', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',    subfontIndex=3))

TC   = HexColor('#0052D9')   # 腾讯蓝
INK  = HexColor('#1a1a1a')
GRAY = HexColor('#5a6068')
LINE = HexColor('#e6e9ee')
LBG  = HexColor('#f4f6fa')

W, H = A4

# 段落样式
title  = ParagraphStyle('t', fontName='HeiB', fontSize=20, leading=27, textColor=INK)
sub    = ParagraphStyle('s', fontName='Hei',  fontSize=10.5, leading=15, textColor=GRAY)
h2     = ParagraphStyle('h2',fontName='HeiB', fontSize=12.5, leading=18, textColor=TC, spaceBefore=4, spaceAfter=3)
body   = ParagraphStyle('b', fontName='Hei',  fontSize=10.2, leading=18, textColor=HexColor('#2b2f36'),
                        spaceAfter=4, firstLineIndent=21)
bodyni = ParagraphStyle('bn',fontName='Hei',  fontSize=10.2, leading=18, textColor=HexColor('#2b2f36'), spaceAfter=2)

class HeaderBar(Flowable):
    """顶部品牌色条 + 标识"""
    def __init__(self, w): self.w=w; self.h=4
    def draw(self):
        self.canv.setFillColor(TC); self.canv.rect(0,0,self.w,self.h,fill=1,stroke=0)

class SectionNum(Flowable):
    """带编号方块的小节标题"""
    def __init__(self, num, text, w):
        self.num=num; self.text=text; self.w=w; self.h=22
    def draw(self):
        c=self.canv
        c.setFillColor(TC); c.roundRect(0,0,18,18,3,fill=1,stroke=0)
        c.setFillColor(HexColor('#ffffff')); c.setFont('HeiB',10.5)
        c.drawCentredString(9,5,str(self.num))
        c.setFillColor(TC); c.setFont('HeiB',12.5)
        c.drawString(26,4.5,self.text)

def hr(color=LINE, th=0.6):
    t=Table([['']],colWidths=[W-50*mm],rowHeights=[1])
    t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),th,color)]))
    return t

doc = BaseDocTemplate('Offer捕手-方案说明文档.pdf', pagesize=A4,
                      leftMargin=25*mm, rightMargin=25*mm, topMargin=18*mm, bottomMargin=18*mm)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='n')

def footer(canvas, d):
    canvas.saveState()
    canvas.setFont('Hei',8); canvas.setFillColor(HexColor('#9aa0a8'))
    canvas.drawString(d.leftMargin, 12*mm, 'Offer捕手 · 学生求职匹配智能体 · 作业方案说明')
    canvas.drawRightString(W-d.rightMargin, 12*mm, '第 %d 页' % d.page)
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
    canvas.line(d.leftMargin,15*mm,W-d.rightMargin,15*mm)
    canvas.restoreState()

doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=footer)])

S = []
S.append(HeaderBar(doc.width)); S.append(Spacer(1,10))
S.append(Paragraph('「Offer捕手」学生求职匹配智能体', title))
S.append(Spacer(1,3))
S.append(Paragraph('作业方案说明文档 ｜ 腾讯 AI-HR 线上实战营', sub))
S.append(Spacer(1,8)); S.append(hr(TC,1.2)); S.append(Spacer(1,12))

def sec(n, t):
    S.append(SectionNum(n,t,doc.width)); S.append(Spacer(1,7))

# 一、问题诊断
sec('一','问题诊断')
S.append(Paragraph('当前高校学生在求职过程中普遍面临三类核心痛点。其一，<b>海量岗位筛选效率低</b>：招聘平台岗位动辄上万，学生缺乏快速定位匹配岗位的工具，往往在海量信息中盲目投递，时间成本高、命中率低。其二，<b>简历与岗位匹配度不明确</b>：学生难以判断自身背景与目标岗位的契合程度，常出现"广撒网、低回应"的困境，求职信心受挫。其三，<b>简历优化无方向</b>：多数学生不了解岗位 JD 的关键考察维度，简历表述偏过程化、缺乏量化成果，难以通过企业初筛环节。',body))
S.append(Spacer(1,8))

# 二、方案设计
sec('二','方案设计')
S.append(Paragraph('「Offer捕手」围绕"信息录入—智能匹配—优化诊断"主线，构建一站式求职辅助闭环，由四个模块协同解决上述痛点。',body))
S.append(Paragraph('<b>信息录入模块</b>支持简历文本粘贴与结构化表单两种方式，通过技能标签选择器、实时校验与完成度进度条降低录入门槛，沉淀出标准化的能力画像。<b>岗位智能匹配模块</b>基于能力、求职意向与地点等多维度加权打分，输出带匹配度百分比、匹配亮点与排序筛选的岗位推荐列表，帮助学生从海量岗位中精准锁定目标。<b>简历优化诊断模块</b>针对目标岗位生成整体匹配度评分、关键项分析与待优化点，并提供"动作+数据+结果"结构的可直接套用润色话术，让优化有据可依。<b>导出与历史记录模块</b>支持报告一键导出与本地留存，方便学生复盘迭代。',body))
S.append(Spacer(1,8))

# 三、技术选型
sec('三','技术选型')
S.append(Paragraph('前端采用 <b>HTML + Tailwind CSS + 原生 JavaScript</b> 的单页应用架构，以模拟数据实现全部功能，无复杂后端依赖。选型理由有三：Tailwind 原子化样式便于快速实现腾讯系简约商务风与一致的设计语言；原生 JS 零构建依赖、加载轻量、可维护性强；单文件结构便于演示与二次修改。',body))
S.append(Paragraph('在部署适配上，项目为纯静态资源，可直接在<b>腾讯云 Cloud Studio</b> 中打开，通过内置的静态服务器（如 <font name="HeiB">python -m http.server</font> 或 Live Server 插件）一键启动，并经平台端口转发生成公网预览链接即时访问，无需配置数据库与服务端环境，部署成本极低。',body))
S.append(Spacer(1,8))

# 四、效果评估
sec('四','效果评估')
S.append(Paragraph('该智能体从效率与精准度两个层面提升学生求职表现。在<b>求职效率</b>上，多维匹配与排序筛选将原本耗时的人工岗位检索压缩为秒级推荐，显著减少盲目投递；在<b>简历初筛命中率</b>上，诊断模块对齐岗位关键词、补强量化成果，预计可帮助学生简历与目标岗位的匹配度评分及初筛通过率获得明显提升。整体而言，「Offer捕手」将分散的求职动作整合为数据驱动的标准化流程，让学生求职更高效、更有方向。',body))

doc.build(S)
print("PDF built")
