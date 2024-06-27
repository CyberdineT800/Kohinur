from utils.db.postgres import Database

class Teachers(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Teachers (
            teacher_Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            Teacher_FullName TEXT,
            teacher_Subject_Id BIGINT,
            teacher_Phone TEXT,
            teacher_Username TEXT,
            teacher_Chat_id TEXT,
            teacher_Salary DECIMAL
        );
        """
        await self.execute(sql, execute=True)

    async def add_teacher(self, data):
        columns = ["Teacher_FullName", "teacher_Subject_Id", "teacher_Phone", 
                   "teacher_Username", "teacher_Chat_id", "teacher_Salary"]
        placeholders = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
        sql = f"INSERT INTO Teachers ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
    
        values = [
            data['teacher_fullname'],
            data['teacher_subject_id'],
            data['teacher_phone'],
            data['teacher_username'],
            data['teacher_chat_id'],
            data['teacher_salary']
        ]
    
        return await self.execute(sql, *values, fetchrow=True)


    async def update_teacher(self, data):
        sql = """
        UPDATE Teachers
        SET  
            Teacher_FullName = $2,
            teacher_Subject_Id = $3,
            teacher_Phone = $4,
            teacher_Username = $5,
            teacher_Chat_id = $6,
            teacher_Salary = $7
        WHERE teacher_Id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['teacher_id'],
                                  data['teacher_fullname'],
                                  data['teacher_subject_id'],
                                  data['teacher_phone'],
                                  data['teacher_username'],
                                  data['teacher_chat_id'],
                                  data['teacher_salary'],
                                  fetchrow=True)

    async def select_all_teachers(self):
        sql = "SELECT * FROM Teachers"
        return await self.execute(sql, fetch=True)

    async def select_teacher(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items()}
        sql = "SELECT * FROM Teachers WHERE 1=1 AND "
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

    async def count_teachers(self):
        sql = "SELECT COUNT(*) FROM Teachers"
        return await self.execute(sql, fetchval=True)
    
    async def delete_teacher_by_id(self, teacher_id):
        sql = "DELETE FROM Teachers WHERE teacher_id = $1"
        await self.execute(sql, teacher_id, execute=True)

    async def upsert_teacher(self, data):
        if 'teacher_id' in data:
            updated_teacher = await self.update_teacher(data)
            if updated_teacher:
                return updated_teacher
        
        new_teacher = await self.add_teacher(data)
        return new_teacher
