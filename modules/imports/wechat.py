import calendar
import csv
from datetime import date
from io import StringIO

import dateparser
from beancount.core import data
from beancount.core.data import Note, Transaction

from .. import accounts
from . import (DictReaderStrip, get_account_by_guess,
               get_income_account_by_guess, replace_flag)
from .base import Base
from .deduplicate import Deduplicate

Account零钱通 = 'Assets:Company:WeChat:Lingqiantong'
Account收入红包 = 'Income:RedBag'
Account支出红包 = 'Expenses:RedBag'
Account余额 = 'Assets:Balances:WeChat'


class WeChat(Base):

    def __init__(self, filename, byte_content, entries, option_map):
        content = byte_content.decode("utf-8-sig")
        lines = content.split("\n")
        if (lines[0].replace(',', '').strip() != '微信支付账单明细'):
            raise Exception('Not WeChat Trade Record!')

        print('Import WeChat: ' + lines[2])
        content = "\n".join(lines[16:len(lines)])
        self.content = content
        self.deduplicate = Deduplicate(entries, option_map)

    def parse(self):
        content = self.content
        f = StringIO(content)
        reader = DictReaderStrip(f, delimiter=',')
        transactions = []
        for row in reader:
            transactions.append(self.gen_transaction(row))
        return transactions

    def gen_transaction(self, row):
        trade_type = row['交易类型']
        trade_amount = row['金额(元)'].replace('¥', '')
        trade_status = row['当前状态']
        trade_time = dateparser.parse(row['交易时间'])
        trade_account = row['支付方式']
        trade_partner = row['交易对方']
        trade_description = row['商品']
        trade_comment = row['备注']

        meta = {}
        meta['trade_time'] = row['交易时间']
        if trade_comment != '/':
            meta['comment'] = trade_comment

        entry = Transaction(meta, trade_time.strftime('%Y-%m-%d'), '*', trade_partner, trade_description,
                            data.EMPTY_SET,
                            data.EMPTY_SET, [])

        amount1 = trade_amount
        if row['收/支'] == '支出':
            amount1 = '-' + trade_amount
        data.create_simple_posting(entry, accounts.get_reality_account(row, 'wechat', trade_account), amount1,
                                       'CNY')

        if trade_type == '商户消费' or trade_type == '扫二维码付款':
            data.create_simple_posting(entry, accounts.get_account(trade_partner, trade_description, trade_time, trade_comment),
                                       trade_amount, 'CNY')


        return entry

# print("Importing {} at {}".format(row['商品'], row['交易时间']))
#             meta = {}
#             time = dateparser.parse(row['交易时间'])
#             # meta['wechat_trade_no'] = row['交易单号']
#             meta['trade_time'] = row['交易时间']
#             # meta['timestamp'] = str(time.timestamp()).replace('.0', '')
#             # account = get_account_by_guess(row['交易对方'], row['商品'], time)
#             # flag = "*"
#             amount_string = row['金额(元)'].replace('¥', '')
#             amount = float(amount_string)
#
#             if row['商户单号'] != '/':
#                 meta['shop_trade_no'] = row['商户单号']
#
#             if row['备注'] != '/':
#                 meta['note'] = row['备注']
#
#             meta = data.new_metadata(
#                 'beancount/core/testing.beancount',
#                 12345,
#                 meta
#             )
#             entry = Transaction(
#                 meta,
#                 date(time.year, time.month, time.day),
#                 '*',
#                 row['交易对方'],
#                 row['商品'],
#                 data.EMPTY_SET,
#                 data.EMPTY_SET, []
#             )
#
#             status = row['当前状态']
#
#             if status == '支付成功' or status == '朋友已收钱' or status == '已全额退款' or '已退款' in status:
#                 if '转入零钱通' in row['交易类型']:
#                     entry = entry._replace(payee='')
#                     entry = entry._replace(narration='转入零钱通')
#                     data.create_simple_posting(
#                         entry, Account零钱通, amount_string, 'CNY')
#                 else:
#                     if '微信红包' in row['交易类型']:
#                         account = Account支出红包
#                         if entry.narration == '/':
#                             entry = entry._replace(narration=row['交易类型'])
#                     else:
#                         account = get_account_by_guess(
#                             row['交易对方'], row['商品'], time)
#                     # if account == "Unknown":
#                     #	entry = replace_flag(entry, '!')
#                     if status == '已全额退款':
#                         amount_string = '-' + amount_string
#                     data.create_simple_posting(
#                         entry, account, amount_string, 'CNY')
#                 data.create_simple_posting(
#                     entry, accounts_map[row['支付方式']], None, None)
#             elif row['当前状态'] == '已存入零钱':
#                 if '微信红包' in row['交易类型']:
#                     if entry.narration == '/':
#                         entry = entry._replace(narration=row['交易类型'])
#                     data.create_simple_posting(entry, Account收入红包, None, 'CNY')
#                 else:
#                     income = get_income_account_by_guess(
#                         row['交易对方'], row['商品'], time)
#                     if income == 'Income:Unknown':
#                         entry = replace_flag(entry, '!')
#                     data.create_simple_posting(entry, income, None, 'CNY')
#                 data.create_simple_posting(
#                     entry, Account余额, amount_string, 'CNY')
#             else:
#                 print('Unknown row', row)
#
#             # b = printer.format_entry(entry)
#             # print(b)
#             if not self.deduplicate.find_duplicate(entry, amount, 'wechat_trade_no'):
#                 transactions.append(entry)
#
#         self.deduplicate.apply_beans()
