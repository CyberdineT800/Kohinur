from utils.db.postgres import Database

class TestFiles(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS test_files (
            test_file_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            test_subject_id INT,
            test_teacher_id INT,
            test_file_tid TEXT,
            test_file_name TEXT
        );
        """
        await self.execute(sql, execute=True)

    async def add_test_file(self, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"${i}" for i in range(1, len(data) + 1))
        sql = f"INSERT INTO test_files ({columns}) VALUES ({placeholders}) RETURNING *"
        return await self.execute(sql, *data.values(), fetchrow=True)

    async def update_test_file(self, data):
        sql = """
        UPDATE test_files
        SET  
            test_subject_id = $2,
            test_teacher_id = $3,
            test_file_tid = $4,
            test_file_name = $5
        WHERE test_file_id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['test_file_id'],
                                  data['test_subject_id'],
                                  data['test_teacher_id'],
                                  data['test_file_tid'],
                                  data['test_file_name'],
                                  fetchrow=True)

    async def select_all_test_files(self):
        sql = "SELECT * FROM test_files"
        return await self.execute(sql, fetch=True)

    async def select_test_files(self, **kwargs):
        sql = "SELECT * FROM test_files WHERE 1=1 AND "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def delete_test_file_by_id(self, test_file_id):
        sql = "DELETE FROM test_files WHERE test_file_id = $1"
        await self.execute(sql, test_file_id, execute=True)

    def format_args(self, sql, parameters):
        sql_parts = []
        args = []
        for idx, (key, value) in enumerate(parameters.items(), 1):
            sql_parts.append(f"{key} = ${idx}")
            args.append(value)
        sql += " AND ".join(sql_parts)
        return sql, args
