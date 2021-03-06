# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import cStringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
import time
from dbfpy import dbf
import os
import random

def index():
    form=SQLFORM.factory(
        Field('jacketno','string', label='Jacket Number', requires=IS_NOT_EMPTY()),
        Field('dbffile','upload',uploadfolder=os.path.join(request.folder,'uploads'), label='DBF File', requires=IS_NOT_EMPTY()),
        formstyle="divs", formname="dist_rep"
    )
    if form.process().accepted:
        session.flash = 'Form Accepted'
        redirect(URL('create_labels_pdf', args=[form.vars.jacketno, form.vars.dbffile]))
    elif form.errors:
        response.flash = 'Form Has Errors'
    else:
        response.flash = 'Please Fill the Form'

    return dict(form=form)


def create_labels_pdf():
    jacket = request.args(0)
    table = dbf.Dbf(os.path.join(request.folder,'uploads',request.args(1)))

    buffer = cStringIO.StringIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    top_bottom_margin = 1.0*inch
    left_right_margin = 0.30*inch
    line_space = 0.1875*inch
    scnd_clmn = width/2
    rec_size = 1.5*inch

    c.translate(0, height - line_space)
    c.setFont("Helvetica", 11)
    c.drawCentredString(width/2,-line_space * 1,"Jacket: "+str(jacket))
    c.drawCentredString(width/2,-line_space * 2,"Date: "+time.strftime("%m/%d/%Y"))

    total_count = 0
    rec_count = 0
    pair_count = -1
    for item in table:
        c.setFont("Helvetica", 10)
        if rec_count%2 == 0:
            pair_count+=1
            c.drawString(left_right_margin, -top_bottom_margin - (0 * line_space) - (rec_size * pair_count), item['AGENCY'] if item['AGENCY'] else '')
            c.drawString(left_right_margin, -top_bottom_margin - (1 * line_space) - (rec_size * pair_count), item['ADDRESS1'] if item['ADDRESS1'] else '')
            c.drawString(left_right_margin, -top_bottom_margin - (2 * line_space) - (rec_size * pair_count), item['ADDRESS2'] if item['ADDRESS2'] else '')
            c.drawString(left_right_margin, -top_bottom_margin - (3 * line_space) - (rec_size * pair_count), item['ADDRESS3'] if item['ADDRESS3'] else '')
            c.drawString(left_right_margin, -top_bottom_margin - (4 * line_space) - (rec_size * pair_count), item['ADDRESS4'] if item['ADDRESS4'] else '')
        else:
            c.drawString(scnd_clmn + left_right_margin, -top_bottom_margin - (0 * line_space) - (rec_size * pair_count), item['AGENCY'] if item['AGENCY'] else '')
            c.drawString(scnd_clmn + left_right_margin, -top_bottom_margin - (1 * line_space) - (rec_size * pair_count), item['ADDRESS1'] if item['ADDRESS1'] else '')
            c.drawString(scnd_clmn + left_right_margin, -top_bottom_margin - (2 * line_space) - (rec_size * pair_count), item['ADDRESS2'] if item['ADDRESS2'] else '')
            c.drawString(scnd_clmn + left_right_margin, -top_bottom_margin - (3 * line_space) - (rec_size * pair_count), item['ADDRESS3'] if item['ADDRESS3'] else '')
            c.drawString(scnd_clmn + left_right_margin, -top_bottom_margin - (4 * line_space) - (rec_size * pair_count), item['ADDRESS4'] if item['ADDRESS4'] else '')
        rec_count+=1
        if rec_count > 11:
            rec_count = 0
            pair_count = -1
            c.showPage()
            c.translate(0, height - line_space)
            c.setFont("Helvetica", 11)
            c.drawCentredString(width/2,-line_space * 1,"Jacket: "+str(jacket))
            c.drawCentredString(width/2,-line_space * 2,"Date: "+time.strftime("%m/%d/%Y"))

    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    header = {'Content-Disposition': 'attachment; filename=' + str(jacket) + '_labels.pdf'}
    #        header = {'Content-Type': 'application/pdf'}

    response.headers.update(header)
    
    return pdf


def create_receipts_pdf():
    title = request.args(0)
    upfile=os.path.join(request.folder,'uploads',request.args(1))
    table = dbf.Dbf(upfile)

    buffer = cStringIO.StringIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    line_space = 11
    third_page = height/3 - 5
    end_width = width - 25

    for item in table:
        c.translate(0, height - line_space)
        time.sleep(0.01)
        rec_num = str.format('{0:.2f}',time.time())
        for pos in range(0,3):
            c.setFont("Helvetica", 11)
            c.drawCentredString(width/2, -line_space - (third_page * pos), "UNITED STATES GOVERNMENT PUBLISHING OFFICE")
            c.drawCentredString(width/2, -2*(line_space) - (third_page * pos), "DELIVERY RECEIPT")
            c.setFont("Helvetica", 10)
            c.drawString(15*mm, -(3 * line_space) - (third_page * pos),"JACKET")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35*mm, -(3 * line_space) - (third_page * pos),str(item['BILLINGJKT']) + "  00000")
            c.setFont("Helvetica", 10)
            c.drawString(60*mm, -(3 * line_space) - (third_page * pos),"REQ. NO.")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(80*mm, -(3 * line_space) - (third_page * pos),"00000")
            c.setFont("Helvetica", 10)
            c.drawString(140*mm, -(3 * line_space) - (third_page * pos),"RECEIPT NO.")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(175*mm, -(3 * line_space) - (third_page * pos),rec_num)
            c.setFont("Helvetica", 10)
            c.drawString(15*mm, -(5 * line_space) - (third_page * pos),"DELIVER TO:")
            c.drawString(140*mm, -(5 * line_space) - (third_page * pos), "DATE:")
            c.drawString(140*mm, -(6 * line_space) - (third_page * pos), "PREPARED BY:")
            c.drawString(140*mm, -(7 * line_space) - (third_page * pos), "AGENCY BAC:")
            c.drawString(140*mm, -(8 * line_space) - (third_page * pos), "AGENCY JACKET:")
            c.drawString(140*mm, -(9 * line_space) - (third_page * pos), "AGENCY REQ.:")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(175*mm,-(5 * line_space) - (third_page * pos), time.strftime("%m/%d/%y"))
#                c.drawString(175*mm,-(6 * line_space) - (third_page * pos), auth.user.first_name[0] + '. ' + auth.user.last_name)
            c.drawString(175*mm,-(7 * line_space) - (third_page * pos), item['BAC'] if item['BAC'] else '')
            c.drawString(175*mm,-(8 * line_space) - (third_page * pos), str(item['OPENJKT'])[0:3] + '-' + str(item['OPENJKT'])[3:6] if item['OPENJKT'] and str(item['OPENJKT'])[0:2] != '00' else '')
            c.drawString(175*mm,-(9 * line_space) - (third_page * pos), item['REQ'] if item['REQ'] else '')
            c.drawString(40*mm,-(5 * line_space) - (third_page * pos), item['AGENCY'] if item['AGENCY'] else '')
            c.drawString(40*mm,-(6 * line_space) - (third_page * pos), item['ADDRESS1'] if item['ADDRESS1'] else '')
            c.drawString(40*mm,-(7 * line_space) - (third_page * pos), item['ADDRESS2'] if item['ADDRESS2'] else '')
            c.drawString(40*mm,-(8 * line_space) - (third_page * pos), item['ADDRESS3'] if item['ADDRESS3'] else '')
            c.drawString(40*mm,-(9 * line_space) - (third_page * pos), item['ADDRESS4'] if item['ADDRESS4'] else '')
            c.setFont("Helvetica", 10)
            c.line(15*mm, -(10 * line_space) - (third_page * pos), end_width, -(10 * line_space) - (third_page * pos))
            c.drawCentredString(152*mm, -(11 * line_space) - (third_page * pos), "NUMBER")
            c.drawCentredString(176*mm, -(11 * line_space) - (third_page * pos), "NUMBER")
            c.drawCentredString(198*mm, -(11 * line_space) - (third_page * pos), "MISC.")

            c.drawCentredString(27*mm,-(12 * line_space) - (third_page * pos), "QUANTITY")
            c.drawCentredString(90*mm,-(12 * line_space) - (third_page * pos), "DESCRIPTION OR TITLE")
            c.drawCentredString(152*mm,-(12 * line_space) - (third_page * pos), "PACKAGES")
            c.drawCentredString(176*mm,-(12 * line_space) - (third_page * pos), "CARTONS")
            c.drawCentredString(198*mm,-(12 * line_space) - (third_page * pos), "OTHER")
            c.line(15*mm,-(12 * line_space+2) - (third_page * pos), end_width, -(12 * line_space+2) - (third_page * pos))
            c.line(15*mm,-(14 * line_space+2) - (third_page * pos), end_width, -(14 * line_space+2) - (third_page * pos))
            c.line(40*mm,-(10 * line_space) - (third_page * pos), 40*mm, -(14 * line_space+2) - (third_page * pos))
            c.line(width*2/3 - 5*mm,-(10 * line_space) - (third_page * pos), width*2/3 - 5*mm,-(14 * line_space+2) - (third_page * pos))
            c.line(width*2/3 + 20*mm,-(10 * line_space) - (third_page * pos), width*2/3 + 20*mm,-(14 * line_space+2) - (third_page * pos))
            c.line(width*2/3 + 43*mm,-(10 * line_space) - (third_page * pos), width*2/3 + 43*mm,-(14 * line_space+2) - (third_page * pos))
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(27*mm, -(14 * line_space) - (third_page * pos),  str(item['HEARG']) if item['HEARG'] else '')
            c.drawCentredString(90*mm, -(14 * line_space) - (third_page * pos),  str(title))

            c.setFont("Helvetica", 10)
            c.drawString(15*mm,-(16 * line_space) - (third_page * pos),"CHECKER")
            c.line(37*mm,-(16 * line_space + 1*mm) - (third_page * pos), end_width/2 + 5*mm, -(16 * line_space+ 1*mm) - (third_page * pos))
            c.drawString(end_width/2 + 10*mm,-(16 * line_space) - (third_page * pos),"REC. IN DELIVERY")
            c.line(end_width/2 + 43*mm,-(16 * line_space + 1*mm) - (third_page * pos), end_width, -(16 * line_space + 1*mm) - (third_page * pos))
            c.drawString(15*mm,-(18 * line_space) - (third_page * pos),"MESSENGER")
            c.line(37*mm,-(18 * line_space + 1*mm) - (third_page * pos), end_width/2 + 5*mm,-(18 * line_space + 1*mm) - (third_page * pos))
            c.line(end_width/2 + 10*mm,-(18 * line_space + 1*mm) - (third_page * pos), end_width,-(18 * line_space + 1*mm) - (third_page * pos))
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(end_width/2 + 12*mm,-(19 * line_space + 1*mm) - (third_page * pos),"SIGNATURE OF PERSON RECEIVING")
            c.drawString(end_width-10*mm,-(19 * line_space + 1*mm) - (third_page * pos),"DATE")
            c.setFont("Helvetica", 9)
            if pos == 0:
                c.drawCentredString(width/2,-(20 * line_space + 1*mm) - (third_page * pos), "(Control Copy)")
            elif pos == 1:
                c.drawCentredString(width/2,-(20 * line_space + 1*mm) - (third_page * pos), "(Customer Copy)")
            elif pos == 2:
                c.drawCentredString(width/2,-(20 * line_space + 1*mm) - (third_page * pos), "(Delivery Copy)")
        c.showPage()
        c.save()

    pdf = buffer.getvalue()
    buffer.close()

    header = {'Content-Disposition': 'attachment; filename=' + str(title) + '_receipts.pdf'}
#        header = {'Content-Type': 'application/pdf'}

    response.headers.update(header)
    return pdf


def create_pdf():
    pdf = None
    jacket = None

    form=SQLFORM.factory(
        Field('title','string', label='Description or Title', requires=IS_NOT_EMPTY()),
        Field('dbffile','upload',uploadfolder=os.path.join(request.folder,'uploads'), label='DBF File', requires=IS_NOT_EMPTY()),
        formstyle="divs", formname="dist_rep"
    )
    if form.process().accepted:
        session.flash = 'Form Accepted'
        redirect(URL('create_receipts_pdf', args=[form.vars.title, form.vars.dbffile]))
    elif form.errors:
        response.flash = 'Form Has Errors'
    else:
        response.flash = 'Please Fill the Form'

    return dict(form=form)
