from utils.db.postgres import Database

class Students(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Students (
            student_Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            student_FullName TEXT,
            student_Phone TEXT,
            student_Username TEXT,
            student_Chat_id TEXT,
            student_Group_id BIGINT
        );
        """
        await self.execute(sql, execute=True)

    async def add_student(self, data):
        columns = ["student_FullName", "student_Phone", "student_Username", 
                   "student_Chat_id", "student_Group_id"]
        placeholders = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
        sql = f"INSERT INTO Students ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
    
        values = [
            data['student_fullname'],
            data['student_phone'],
            data['student_username'],
            data['student_chat_id'],
            data['student_group_id']
        ]
    
        return await self.execute(sql, *values, fetchrow=True)

    async def update_student(self, data):
        sql = """
        UPDATE Students
        SET  
            student_FullName = $2,
            student_Phone = $3,
            student_Username = $4,
            student_Chat_id = $5,
            student_Group_id = $6
        WHERE student_Id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['student_id'],
                                  data['student_fullname'],
                                  data['student_phone'],
                                  data['student_username'],
                                  data['student_chat_id'],
                                  data['student_group_id'],
                                  fetchrow=True)

    async def select_all_students(self):
        sql = "SELECT * FROM Students"
        return await self.execute(sql, fetch=True)

    async def select_student(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items()}
        sql = "SELECT * FROM Students WHERE 1=1 AND "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    def format_args(self, sql, parameters):
        sql_parts = []
        args = []
        for idx, (key, value) in enumerate(parameters.items(), 1):
            sql_parts.append(f"{key} = ${idx}")
            args.append(value)
        sql += " AND ".join(sql_parts)
        return sql, args
    
    async def select_students_by_group(self, student_group_id):
        sql = "SELECT * FROM Students WHERE student_Group_id = $1"
        return await self.execute(sql, student_group_id, fetch=True)

    async def count_students(self):
        sql = "SELECT COUNT(*) FROM Students"
        return await self.execute(sql, fetchval=True)
    
    async def delete_student_by_id(self, student_id):
        sql = "DELETE FROM Students WHERE student_Id = $1"
        await self.execute(sql, student_id, execute=True)

    async def upsert_student(self, data):
        if 'student_id' in data:
            updated_student = await self.update_student(data)
            if updated_student:
                return updated_student
        
        new_student = await self.add_student(data)
        return new_student

    async def count_students_by_group(self, student_group_id):
        sql = "SELECT COUNT(*) FROM Students WHERE student_Group_id = $1"
        return await self.execute(sql, student_group_id, fetchval=True)