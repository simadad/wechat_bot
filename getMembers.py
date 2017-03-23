import itchat
import openpyxl


def get_members(name):
    rooms = itchat.search_chatrooms(name=name)
    username = rooms[0]['UserName']
    print(username)
    room_info = itchat.update_chatroom(userName=username)
    members_info = room_info['MemberList']
    for m in members_info:
        yield m['DisplayName'], m['NickName'], m['UserName']


def save_members(names, file=None):
    if file:
        wb = openpyxl.load_workbook(file)
    else:
        wb = openpyxl.Workbook()
    ws = wb.active
    row = 1
    for name in names:
        ws.cell(row=row, column=1).value = name[0]
        ws.cell(row=row, column=2).value = name[1]
        ws.cell(row=row, column=3).value = name[2]
        row += 1
    wb.save('members.xlsx')

