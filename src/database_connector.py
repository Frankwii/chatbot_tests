import mysql.connector

class DatabaseConnector():
    def __init__(self, db_config: dict[str,str]):
        self.__connection=mysql.connector.connect(**db_config)

    def __execute_query(self, query:str, params:str|tuple[str]|None=None):
        """
        Takes a (possibly parametrized) query and executes it handling errors in the execution. A parametrized query simply offers a way to safely insert strings with possibly conflictive characters. For instance, the string "The UK's Cheapest Energy" could raise an error because of the quotation inside if not properly escaped to "The UK\'s Cheapest Energy".

        Args:
            - query (str): The parametrized query (i.e. with an '%s' as a placeholder)
            - params (str|tuple[str]): The parameters to be substituted in; in order.
        """
        if isinstance(params, str):
            params=(params,)
        cursor = self.__connection.cursor(buffered=True) # MariaDB complains without the buffered=True
    
        try:
            cursor.execute(query, params)
            self.__connection.commit()
        except Exception as e:
            print("Couldn't process query!")
            print("=========QUERY=========")
            print(query)
            print("=========PARAM=========")
            print(params)
            print("=========ERROR=========")
            print(e)
            print("=======================")
    
        data=None
        if cursor.with_rows:
            data=cursor.fetchall()
        cursor.close()
        self.__connection.close()
    
        return [] if data is None else data

    def get_table_schema(self, table_name:str):
        query=f"DESCRIBE `{table_name}`"
        return self.__execute_query(query=query, params=None)

    # TODO
    def get_database_schema(self):
        pass

