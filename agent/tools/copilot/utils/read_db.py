import pandas as pd
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

tables_data = None


def get_all_table_names(engine):
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_rows_from_all_tables(engine, tables, num=3):
    # 获取所有表名
    inspector = inspect(engine)
    if not tables:
        table_names = inspector.get_table_names()
    else:
        table_names = tables

    # 准备一个字典来存储每个表的前5行数据
    first_five_rows = {}

    # 遍历所有表名
    for table_name in table_names:
        try:
            # 构造查询语句，限制返回5行
            query = text(f"SELECT * FROM {table_name} LIMIT {num}")

            # 使用 pandas 读取查询结果
            with engine.connect() as connection:
                df = pd.read_sql(query, connection)

            # 将结果存储到字典中
            first_five_rows[table_name] = df

        except SQLAlchemyError as e:
            # 如果发生错误，打印错误信息并继续处理下一个表
            print(f"An error occurred while fetching data from table {table_name}: {e}")
            continue

    return first_five_rows


def get_foreign_keys(engine, tables):
    inspector = inspect(engine)
    if not tables:
        table_names = inspector.get_table_names()
    else:
        table_names = tables
    foreign_keys = {}
    for table_name in table_names:
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            foreign_keys[table_name] = {}
            for fk in fks:
                for i in range(len(fk['constrained_columns'])):
                    foreign_keys[table_name][table_name + "." + fk['constrained_columns'][i]] = \
                        fk['referred_table'] + "." + fk['referred_columns'][i]

    return foreign_keys


def get_table_and_column_comments(engine, tables):
    inspector = inspect(engine)
    if not tables:
        table_names = inspector.get_table_names()
    else:
        table_names = tables
    table_comments = {}
    column_comments = {}

    for table_name in table_names:
        table_comment = inspector.get_table_comment(table_name)
        if table_comment['text'] is not None:
            table_comments[table_name] = table_comment['text']
        columns = inspector.get_columns(table_name)
        column_comments[table_name] = {}
        for column in columns:
            if column['comment'] is not None:
                column_comments[table_name][column['name']] = column['comment']
        if not column_comments[table_name]:
            del column_comments[table_name]
    table_comments = {k: v for k, v in table_comments.items() if v is not None}
    return [table_comments, column_comments]


def get_table_creation_statements(engine, tables, simple=False):
    inspector = inspect(engine)
    if not tables:
        table_names = inspector.get_table_names()
    else:
        table_names = tables
    creation_statements = {}

    for table_name in table_names:
        # 获取表的列信息
        columns = inspector.get_columns(table_name)
        # 获取表的主键信息
        primary_keys = inspector.get_pk_constraint(table_name)
        # 获取表的外键信息
        foreign_keys = inspector.get_foreign_keys(table_name)
        # 获取表的索引信息
        # indexes = inspector.get_indexes(table_name)

        # 开始构建建表语句
        create_table_statement = f"CREATE TABLE {table_name} (\n"

        # 添加列定义
        column_definitions = []
        for column in columns:
            if not simple:
                column_def = f"    {column['name']} {column['type']}"
                if not column['nullable']:
                    column_def += " NOT NULL"
                if column['default'] is not None:
                    column_def += f" DEFAULT {column['default']}"
            else:
                column_def = f"    {column['name']} {column['type']}"
            # # 添加列的注释
            # if 'comment' in column and column['comment']:
            #     column_def += f" COMMENT '{column['comment']}'"
            column_definitions.append(column_def)

        if not simple:
            # 添加主键定义
            if primary_keys['constrained_columns']:
                pk_columns = ", ".join(primary_keys['constrained_columns'])
                column_definitions.append(f"    PRIMARY KEY ({pk_columns})")

            # 添加外键定义
            for fk in foreign_keys:
                fk_columns = ", ".join(fk['constrained_columns'])
                referred_table = fk['referred_table']
                referred_columns = ", ".join(fk['referred_columns'])
                column_definitions.append(
                    f"    FOREIGN KEY ({fk_columns}) REFERENCES {referred_table} ({referred_columns})")

        # 将列定义添加到建表语句中
        create_table_statement += ",\n".join(column_definitions)
        create_table_statement += "\n);"

        # # 添加索引定义
        # for index in indexes:
        #     if not index['unique']:
        #         index_columns = ", ".join(index['column_names'])
        #         create_table_statement += f"\nCREATE INDEX {index['name']} ON {table_name} ({index_columns});"
        #     else:
        #         index_columns = ", ".join(index['column_names'])
        #         create_table_statement += f"\nCREATE UNIQUE INDEX {index['name']} ON {table_name} ({index_columns});"

        # 将建表语句存储到字典中
        creation_statements[table_name] = create_table_statement

    return creation_statements



# def get_table_creation_statements_2(engine):
#     creation_statements = {}
#     with engine.connect() as connection:
#         # 获取所有表名
#         table_names = inspect(engine).get_table_names()
#         for table_name in table_names:
#             # 使用 SHOW CREATE TABLE 获取建表语句
#             query = text(f"SHOW CREATE TABLE {table_name}")
#             result = connection.execute(query).fetchone()
#             if result:
#                 # 结果中的第二列是建表语句
#                 create_table_statement = result[1]
#                 creation_statements[table_name] = create_table_statement
#     return creation_statements


def execute_sql(engine, sql):
    # 使用连接执行SQL语句
    with engine.connect() as connection:
        try:
            # 执行SQL语句
            result = connection.execute(text(sql))
            # 提交事务（对于INSERT、UPDATE、DELETE等操作）
            connection.commit()
            # 返回影响的行数
            return result.rowcount
        except SQLAlchemyError as e:
            # 如果发生错误，回滚事务
            connection.rollback()
            # 打印错误信息
            print(f"An error occurred: {e}")
            raise e


def execute_select(engine, sql):
    try:
        with engine.connect() as connection:
            result_df = pd.read_sql_query(text(sql), connection)
        return result_df
    except SQLAlchemyError as e:
        # 如果发生错误，打印错误信息
        print(f"An error occurred: {e}")
        raise e


if __name__ == "__main__":
    # data = get_data_from_db()
    # print(type(data), "\n")
    # print(data[2][1])
    print("###########################################\n\n")
    print(get_table_creation_statements())

    # for table_name, table_df in mdata.items():
    #     print(f"Table: {table_name}")
    #     print(table_df)
    #     print(type(table_df))
