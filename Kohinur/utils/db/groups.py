from utils.db.postgres import Database

class Groups(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Groups (
            group_Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            group_Name TEXT,
            group_teacher_Id BIGINT,
            group_subject_Id BIGINT,
            group_Days TEXT,
            group_Times TEXT
        );
        """
        await self.execute(sql, execute=True)

    async def add_group(self, data):
        columns = ["group_Name", "group_teacher_Id", "group_subject_Id", 
                   "group_Days", "group_Times"]
        placeholders = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
        sql = f"INSERT INTO Groups ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
    
        values = [
            data['group_name'],
            data['group_teacher_id'],
            data['group_subject_id'],
            data['group_days'],
            data['group_times']
        ]
    
        return await self.execute(sql, *values, fetchrow=True)

    async def update_group(self, data):
        sql = """
        UPDATE Groups
        SET  
            group_Name = $2,
            group_teacher_Id = $3,
            group_subject_Id = $4,
            group_Days = $5,
            group_Times = $6
        WHERE group_Id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['group_id'],
                                  data['group_name'],
                                  data['group_teacher_id'],
                                  data['group_subject_id'],
                                  data['group_days'],
                                  data['group_times'],
                                  fetchrow=True)

    async def select_all_groups(self):
        sql = "SELECT * FROM Groups"
        return await self.execute(sql, fetch=True)

    async def select_all_groups_with_teachers(self):
        sql = """
                SELECT g.*, t.Teacher_FullName AS group_teacher_fullname
                    FROM Groups g
                        JOIN Teachers t ON g.group_teacher_Id = t.teacher_Id
                    ORDER BY g.group_id ASC
              """
        return await self.execute(sql, fetch=True)

    async def select_group(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items()}
        sql = "SELECT * FROM Groups WHERE 1=1 AND "
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
    

    async def select_group_with_teacher(self, group_id):
        sql = """
                SELECT g.*, t.Teacher_FullName AS group_teacher_fullname
                    FROM Groups g
                        JOIN Teachers t ON g.group_teacher_Id = t.teacher_Id
                    WHERE g.group_Id = $1
                LIMIT 1
              """
        return await self.execute(sql, group_id, fetchrow=True)



    async def count_groups(self):
        sql = "SELECT COUNT(*) FROM Groups"
        return await self.execute(sql, fetchval=True)
    
    async def delete_group_by_id(self, group_id):
        sql = "DELETE FROM Groups WHERE group_Id = $1"
        await self.execute(sql, group_id, execute=True)

    async def upsert_group(self, data):
        if 'group_id' in data:
            updated_group = await self.update_group(data)
            if updated_group:
                return updated_group
        
        new_group = await self.add_group(data)
        return new_group


    async def select_groups_by_subject(self, subject_id):
        sql = """
                SELECT g.*, t.Teacher_FullName AS group_teacher_fullname
                    FROM Groups g
                        JOIN Teachers t ON g.group_teacher_Id = t.teacher_Id
                    WHERE g.group_subject_Id = $1
                ORDER BY g.group_id ASC
              """
        return await self.execute(sql, subject_id, fetch=True)
    
    async def select_groups_by_teacher(self, teacher_id):
        sql = """
                SELECT g.*, t.Teacher_FullName AS group_teacher_fullname
                    FROM Groups g
                        JOIN Teachers t ON g.group_teacher_Id = t.teacher_Id
                    WHERE g.group_teacher_Id = $1
                ORDER BY g.group_id ASC
              """
        return await self.execute(sql, teacher_id, fetch=True)
