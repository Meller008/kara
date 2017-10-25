
def tab_html(table, table_head=None, up_template=None, down_template=None):
    tab_h = ""

    if up_template:
        tab_h += up_template

    tab_h += """<style>
           table {
            width: 100%;
            border: 4px double black;
            border-collapse: collapse;
           }
           th {
            text-align: left;
            background: #ccc;
            padding: 5px;
            border: 1px solid black;
           }
           td {
            padding: 2px;
            border: 1px solid black;
           }
           caption{
           font-weight: 800;
           }
          </style>
          <table> """

    if table_head:
        tab_h += "<caption>%s</caption> " % table_head

    tab_h += '<tr>'

    #  Формируем шапку
    for col in range(table.horizontalHeader().count()):
        tab_h += '<th>'
        tab_h += table.horizontalHeaderItem(col).text()
        tab_h += '</th>'
    else:
        tab_h += '</tr>'

    #  Заполняем внутрености
    for row in range(table.rowCount()):
        tab_h += '<tr>'

        for col in range(table.columnCount()):
            tab_h += '<td>'
            if table.item(row, col):
                cell_text = table.item(row, col).text()
            else:
                cell_text = ""
            tab_h += cell_text
            tab_h += '</td>'

        tab_h += '</tr>'

    tab_h += '</table>'

    if down_template:
        tab_h += down_template

    return tab_h


