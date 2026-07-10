# agents/sanction_generator.py
# Simple, reliable PDF — no HRFlowable inside tables

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class SanctionLetterGenerator:

    RED    = colors.HexColor('#C00000')
    DKRED  = colors.HexColor('#8B0000')
    LTRED  = colors.HexColor('#FFF5F5')
    LTGREY = colors.HexColor('#F5F5F5')
    MDGREY = colors.HexColor('#999999')
    DKGREY = colors.HexColor('#333333')
    GREEN  = colors.HexColor('#1A6B2A')
    WHITE  = colors.white

    def run(self, customer: dict, loan_details: dict,
            output_path: str = "sanction_letter.pdf") -> str:

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        story = []
        story += self._letterhead()
        story += self._title(loan_details)
        story += self._ref_row()
        story += self._salutation(customer)
        story += self._borrower_section(customer)
        story += self._loan_section(loan_details)
        story += self._amort_section(loan_details)
        story += self._terms_section()
        story += self._signature_section()

        doc.build(story)
        return output_path

    # helper to make a paragraph style quickly
    def _ps(self, name, font='Helvetica', size=9, color=None,
            align=None, leading=13, indent=0):
        kwargs = dict(fontName=font, fontSize=size, leading=leading, leftIndent=indent)
        if color:
            kwargs['textColor'] = color
        if align is not None:
            kwargs['alignment'] = align
        return ParagraphStyle(name, **kwargs)

    def _letterhead(self):
        # Top red bar
        bar = Table([['']], colWidths=[17*cm], rowHeights=[0.18*cm])
        bar.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1), self.RED)]))

        # Company name + info side by side
        ps_name = self._ps('cn', font='Helvetica-Bold', size=20,
                            color=self.RED, leading=24)
        ps_info = self._ps('ci', size=8, color=self.MDGREY,
                            align=TA_RIGHT, leading=12)
        ps_addr = self._ps('ca', size=8, color=self.MDGREY, leading=12)

        hdr = Table([
            [
                Paragraph('TATA CAPITAL LIMITED', ps_name),
                Paragraph('RBI Registered NBFC<br/>CIN: U65990MH2006PLC166854<br/>www.tatacapital.com', ps_info),
            ]
        ], colWidths=[9*cm, 8*cm])
        hdr.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('PADDING',(0,0),(-1,-1),0),
        ]))

        addr = Paragraph(
            '11th Floor, Tower A, Peninsula Business Park, Lower Parel, Mumbai - 400 013',
            ps_addr
        )

        # Red bottom line using a 1-row table with red background (safe, no HRFlowable)
        rule = Table([['']], colWidths=[17*cm], rowHeights=[0.15*cm])
        rule.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1), self.RED)]))

        return [
            bar,
            Spacer(1, 0.2*cm),
            hdr,
            Spacer(1, 0.08*cm),
            addr,
            Spacer(1, 0.1*cm),
            rule,
            Spacer(1, 0.3*cm),
        ]

    def _title(self, ld):
        ps_t = self._ps('tt', font='Helvetica-Bold', size=13,
                         color=self.DKGREY, leading=18)
        ps_b = self._ps('tb', font='Helvetica-Bold', size=9,
                         color=self.WHITE, align=TA_CENTER, leading=14)

        badge = 'INSTANT APPROVAL' if ld.get('approval_type') == 'INSTANT' else 'APPROVED'

        tbl = Table([
            [Paragraph('PERSONAL LOAN SANCTION LETTER', ps_t),
             Paragraph(badge, ps_b)]
        ], colWidths=[11.5*cm, 5.5*cm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (1,0),(1,0), self.RED),
            ('VALIGN',     (0,0),(-1,-1),'MIDDLE'),
            ('PADDING',    (0,0),(0,0), 0),
            ('PADDING',    (1,0),(1,0), 8),
        ]))
        return [tbl, Spacer(1, 0.25*cm)]

    def _ref_row(self):
        ref    = f"TCL/PL/2025/{datetime.now().strftime('%m%d%H%M%S')}"
        issue  = datetime.now().strftime('%d %B %Y')
        expiry = (datetime.now() + relativedelta(days=30)).strftime('%d %B %Y')

        ps = self._ps('rp', size=9, color=self.DKGREY, leading=13)
        ps_r = self._ps('rpr', size=9, color=self.DKGREY,
                         align=TA_RIGHT, leading=13)

        tbl = Table([
            [Paragraph(f'<b>Ref No:</b>  {ref}', ps),
             Paragraph(f'<b>Issue Date:</b>  {issue}', ps_r)],
            [Paragraph('<b>Validity:</b>  30 days from issue', ps),
             Paragraph(f'<b>Offer Expiry:</b>  {expiry}', ps_r)],
        ], colWidths=[8.5*cm, 8.5*cm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), self.LTGREY),
            ('GRID',      (0,0),(-1,-1), 0.3, colors.HexColor('#DDDDDD')),
            ('PADDING',   (0,0),(-1,-1), 7),
            ('VALIGN',    (0,0),(-1,-1),'MIDDLE'),
        ]))
        return [tbl, Spacer(1, 0.25*cm)]

    def _salutation(self, customer):
        name = customer.get('name', 'Valued Customer')
        ps   = self._ps('sp', size=10, color=self.DKGREY, leading=16)
        return [
            Paragraph(f'Dear <b>{name}</b>,', ps),
            Spacer(1, 0.1*cm),
            Paragraph(
                'We are pleased to inform you that your Personal Loan application with '
                '<b>Tata Capital Limited</b> has been evaluated and <b>sanctioned</b>. '
                'We thank you for choosing Tata Capital as your trusted financial partner.',
                ps
            ),
            Spacer(1, 0.25*cm),
        ]

    def _make_section_header(self, text):
        ps = self._ps('sh', font='Helvetica-Bold', size=9,
                       color=self.WHITE, leading=13)
        tbl = Table([[Paragraph(text, ps), '']],
                    colWidths=[17*cm], rowHeights=[0.7*cm])
        tbl.setStyle(TableStyle([
            ('SPAN',       (0,0),(-1,-1)),
            ('BACKGROUND', (0,0),(-1,-1), self.RED),
            ('PADDING',    (0,0),(-1,-1), 8),
            ('VALIGN',     (0,0),(-1,-1),'MIDDLE'),
        ]))
        return tbl

    def _make_data_table(self, rows, col_widths=None):
        if col_widths is None:
            col_widths = [5.5*cm, 11.5*cm]
        ps_k = self._ps('dk', font='Helvetica-Bold', size=9,
                         color=self.DKGREY, leading=13)
        ps_v = self._ps('dv', size=9, color=self.DKGREY, leading=13)
        ps_g = self._ps('dg', font='Helvetica-Bold', size=9,
                         color=self.GREEN, leading=13)

        table_rows = []
        for key, val, highlight in rows:
            style = ps_g if highlight else ps_v
            table_rows.append([Paragraph(key, ps_k), Paragraph(str(val), style)])

        tbl = Table(table_rows, colWidths=col_widths)
        tbl.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0,0),(-1,-1), [self.WHITE, self.LTGREY]),
            ('GRID',           (0,0),(-1,-1), 0.3, colors.HexColor('#DDDDDD')),
            ('PADDING',        (0,0),(-1,-1), 7),
            ('VALIGN',         (0,0),(-1,-1),'TOP'),
        ]))
        return tbl

    def _borrower_section(self, c):
        rows = [
            ('Full Name',          c.get('name',     'N/A'), False),
            ('Registered Mobile',  c.get('phone',    'N/A'), False),
            ('Email Address',      c.get('email',    'N/A'), False),
            ('Registered Address', c.get('address',  'N/A'), False),
            ('KYC Type',           c.get('kyc_type', 'Aadhaar + PAN'), False),
            ('Employer',           c.get('employer', 'N/A'), False),
        ]
        return [
            self._make_section_header('BORROWER INFORMATION'),
            self._make_data_table(rows),
            Spacer(1, 0.25*cm),
        ]

    def _loan_section(self, ld):
        tenure_mo = ld.get('tenure_months', 36)
        y, m = divmod(tenure_mo, 12)
        tenure_str = (f"{tenure_mo} months ({y} yr)"
                      if m == 0 else f"{tenure_mo} months ({y} yr {m} mo)")

        approval_str = ('Instant Approval - Pre-Approved Limit'
                        if ld.get('approval_type') == 'INSTANT'
                        else 'Approved - Salary Verified')

        rows = [
            ('Loan Amount Sanctioned',  f"Rs. {ld.get('loan_amount',0):,.2f}",         True),
            ('Loan Tenure',             tenure_str,                                      False),
            ('Rate of Interest (p.a.)', f"{ld.get('interest_rate',0)}% p.a. (Reducing Balance)", False),
            ('Monthly EMI',             f"Rs. {ld.get('emi',0):,.2f}",                  True),
            ('Processing Fee',          f"Rs. {ld.get('processing_fee',0):,.2f} (incl. GST)", False),
            ('Total Interest Payable',  f"Rs. {ld.get('total_interest',0):,.2f}",       False),
            ('Total Amount Payable',    f"Rs. {ld.get('total_payable',0):,.2f}",        False),
            ('Credit Score',            f"{ld.get('credit_score',0)} / 900",            False),
            ('Approval Category',       approval_str,                                    False),
            ('Disbursement ETA',        ld.get('disbursement_eta','Within 24 hours'),   False),
        ]

        if ld.get('monthly_salary'):
            rows.insert(-2, ('Monthly Income (Verified)',
                              f"Rs. {ld['monthly_salary']:,.2f}", False))
            rows.insert(-2, ('EMI to Income Ratio',
                              f"{ld.get('emi_to_salary_ratio',0):.1f}% (Max 50%)", False))

        return [
            self._make_section_header('LOAN SANCTION DETAILS'),
            self._make_data_table(rows),
            Spacer(1, 0.25*cm),
        ]

    def _amort_section(self, ld):
        ps_col  = self._ps('ac', font='Helvetica-Bold', size=8,
                            color=self.WHITE, align=TA_CENTER, leading=12)
        ps_num  = self._ps('an', size=8, color=self.DKGREY,
                            align=TA_CENTER, leading=12)
        ps_numb = self._ps('anb', font='Helvetica-Bold', size=8,
                            color=self.DKGREY, align=TA_CENTER, leading=12)
        ps_note = self._ps('nt', size=8, color=self.MDGREY, leading=12)

        headers = [
            Paragraph('EMI #',      ps_col),
            Paragraph('Due Date',   ps_col),
            Paragraph('EMI (Rs.)',  ps_col),
            Paragraph('Principal',  ps_col),
            Paragraph('Interest',   ps_col),
            Paragraph('Balance',    ps_col),
        ]

        rate_m  = ld.get('interest_rate', 12) / 1200
        balance = float(ld.get('loan_amount', 0))
        emi     = float(ld.get('emi', 0))
        start   = date.today().replace(day=5) + relativedelta(months=1)

        data = [headers]
        for i in range(1, 7):
            int_p  = balance * rate_m
            prin_p = emi - int_p
            balance -= prin_p
            due = start + relativedelta(months=i-1)
            data.append([
                Paragraph(str(i),                   ps_numb),
                Paragraph(due.strftime('%d %b %Y'), ps_num),
                Paragraph(f"{emi:,.2f}",            ps_numb),
                Paragraph(f"{prin_p:,.2f}",         ps_num),
                Paragraph(f"{int_p:,.2f}",          ps_num),
                Paragraph(f"{max(balance,0):,.2f}", ps_num),
            ])

        tbl = Table(data, colWidths=[1.5*cm, 3.5*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',     (0,0),(-1,0), self.DKRED),
            ('PADDING',        (0,0),(-1,0), 7),
            ('ROWBACKGROUNDS', (0,1),(-1,-1), [self.WHITE, self.LTRED]),
            ('GRID',           (0,0),(-1,-1), 0.3, colors.HexColor('#DDDDDD')),
            ('PADDING',        (0,1),(-1,-1), 6),
            ('VALIGN',         (0,0),(-1,-1),'MIDDLE'),
        ]))

        note = Paragraph(
            '* First 6 EMIs shown above. Full schedule provided at disbursement. EMI due on 5th of each month.',
            ps_note
        )

        return [
            self._make_section_header('EMI SCHEDULE - First 6 Installments'),
            tbl,
            Spacer(1, 0.1*cm),
            note,
            Spacer(1, 0.25*cm),
        ]

    def _terms_section(self):
        ps_title = self._ps('tt2', font='Helvetica-Bold', size=10,
                             color=self.RED, leading=14)
        ps_term  = self._ps('tm', size=9, color=self.DKGREY,
                             leading=14, indent=12)

        terms = [
            '1.  This sanction letter is valid for <b>30 days</b> from date of issue. Disbursement subject to document verification.',
            '2.  EMI will be auto-debited from registered bank account on due date each month via NACH mandate.',
            '3.  Pre-closure permitted after 6 EMIs. Pre-closure charges of 2%-4% on outstanding principal apply.',
            '4.  Late payment charges: Rs.500 flat + 2% per month on overdue EMI amount.',
            '5.  Loan agreement, NACH mandate and KYC documents must be submitted before disbursement.',
            '6.  Sanction subject to Tata Capital credit policy, RBI guidelines and applicable laws.',
            '7.  Tata Capital reserves the right to withdraw this sanction if information is found inaccurate.',
        ]

        story = [Paragraph('TERMS AND CONDITIONS', ps_title), Spacer(1, 0.1*cm)]
        for t in terms:
            story.append(Paragraph(t, ps_term))
            story.append(Spacer(1, 0.07*cm))
        story.append(Spacer(1, 0.15*cm))
        return story

    def _signature_section(self):
        ps_s  = self._ps('ss',  size=9, color=self.DKGREY, leading=14)
        ps_ln = self._ps('sln', size=9, color=self.MDGREY, leading=14)
        ps_ft = self._ps('sft', size=7.5, color=self.MDGREY,
                          align=TA_CENTER, leading=11)

        # Top divider row (single cell table, not HRFlowable in cell)
        divider = Table([['']], colWidths=[17*cm], rowHeights=[0.08*cm])
        divider.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#DDDDDD'))
        ]))

        # Signature table — use plain text underscores, NO HRFlowable inside
        sig = Table([
            [Paragraph('For <b>Tata Capital Limited</b>', ps_s),
             Paragraph('Borrower Signature', ps_s)],
            [Paragraph(' ', ps_s), Paragraph(' ', ps_s)],
            [Paragraph(' ', ps_s), Paragraph(' ', ps_s)],
            [Paragraph('________________________________', ps_ln),
             Paragraph('________________________________', ps_ln)],
            [Paragraph('Authorised Signatory', ps_s),
             Paragraph('(Borrower / Co-applicant)', ps_s)],
            [Paragraph('Personal Loans Division', ps_s),
             Paragraph('Date: _______________', ps_s)],
        ], colWidths=[8.5*cm, 8.5*cm])
        sig.setStyle(TableStyle([
            ('VALIGN',  (0,0),(-1,-1),'BOTTOM'),
            ('PADDING', (0,0),(-1,-1), 4),
        ]))

        # Footer divider
        foot_div = Table([['']], colWidths=[17*cm], rowHeights=[0.08*cm])
        foot_div.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#DDDDDD'))
        ]))

        footer = Paragraph(
            'System-generated document  |  Helpline: 1860-267-6060  |  '
            'customercare@tatacapital.com  |  www.tatacapital.com',
            ps_ft
        )

        return [
            divider,
            Spacer(1, 0.2*cm),
            sig,
            Spacer(1, 0.2*cm),
            foot_div,
            Spacer(1, 0.1*cm),
            footer,
        ]
    
    