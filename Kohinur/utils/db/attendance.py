from utils.db.postgres import Database

class Attendance(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Attendance (
            attendance_Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            attendance_student_Id BIGINT,
            attendance_group_Id BIGINT,
            attendance_Date DATE,
            attendance_Status TEXT,
            UNIQUE (attendance_student_Id, attendance_group_Id, attendance_Date)
        );
        """
        await self.execute(sql, execute=True)

    async def add_attendance(self, data):
        columns = ["attendance_student_Id", "attendance_group_Id", "attendance_Date", "attendance_Status"]
        placeholders = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
        sql = f"INSERT INTO Attendance ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
    
        values = [
            data['attendance_student_id'],
            data['attendance_group_id'],
            data['attendance_date'],
            data['attendance_status']
        ]
    
        return await self.execute(sql, *values, fetchrow=True)

    async def update_attendance(self, data):
        sql = """
            UPDATE Attendance
                SET  
                    attendance_Status = $4
                WHERE attendance_student_Id = $1 AND attendance_group_Id = $2 AND attendance_Date = $3
            RETURNING *
            """
        return await self.execute(sql,
                                  data['attendance_student_id'],
                                  data['attendance_group_id'],
                                  data['attendance_date'],
                                  data['attendance_status'],
                                  fetchrow=True)

    async def select_all_attendance(self):
        sql = "SELECT * FROM Attendance"
        return await self.execute(sql, fetch=True)

    async def select_attendance(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items()}
        sql = "SELECT * FROM Attendance WHERE 1=1 AND "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    def format_args(self, sql, parameters):
        sql_parts = []
        args = []
        for idx, (key, value) in enumerate(parameters.items(), 1):
            sql_parts.append(f"{key} = ${idx}")
            args.append(value)
        sql += " AND ".join(sql_parts)
        return sql, args

    async def count_attendance(self):
        sql = "SELECT COUNT(*) FROM Attendance"
        return await self.execute(sql, fetchval=True)
    
    async def delete_attendance_by_id(self, attendance_id):
        sql = "DELETE FROM Attendance WHERE attendance_Id = $1"
        await self.execute(sql, attendance_id, execute=True)

    async def upsert_attendance(self, data):
        sql_update = """
            UPDATE Attendance
                SET  
                    attendance_Status = $4
                WHERE attendance_student_Id = $1 AND attendance_group_Id = $2 AND attendance_Date = $3
            RETURNING *
            """
        updated_attendance = await self.execute(sql_update,
                                                data['attendance_student_id'],
                                                data['attendance_group_id'],
                                                data['attendance_date'],
                                                data['attendance_status'],
                                                fetchrow=True)
        if updated_attendance:
            return updated_attendance

        sql_insert = """
            INSERT INTO Attendance (attendance_student_Id, attendance_group_Id, attendance_Date, attendance_Status)
                VALUES ($1, $2, $3, $4)
            RETURNING *
            """
        new_attendance = await self.execute(sql_insert,
                                            data['attendance_student_id'],
                                            data['attendance_group_id'],
                                            data['attendance_date'],
                                            data['attendance_status'],
                                            fetchrow=True)
        return new_attendance
