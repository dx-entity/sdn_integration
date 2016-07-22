import DBConnector


def clean_data(caseid):
    db = DBConnector.DBConnector()
    sql_clean = '''
        delete from b_case_ovs where caseid='{0}'
    '''.format(caseid)

    db.update_all(sql_clean)