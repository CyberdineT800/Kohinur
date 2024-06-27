from utils.db.postgres import Database

class Subjects(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Subjects (
            Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            SubjectName TEXT,
            NumberOfAvailableTests INT DEFAULT 0,
            SubjectPrice DECIMAL
        );
        """
        await self.execute(sql, execute=True)

    async def add_subject(self, name, price):
        sql = "INSERT INTO Subjects (SubjectName, SubjectPrice) VALUES ($1, $2) RETURNING *"
        return await self.execute(sql, name, price, fetchrow=True)

    async def update_subject(self, data):
        sql = """
        UPDATE Subjects
        SET  
            SubjectName = $2,
            NumberOfAvailableTests = $3,
            SubjectPrice = $4
        WHERE Id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['id'],
                                  data['subjectname'],
                                  data['numberofavailabletests'],
                                  data['subjectprice'],
                                  fetchrow=True)

    async def select_all_subjects(self):
        sql = "SELECT * FROM Subjects"
        return await self.execute(sql, fetch=True)
    
    async def select_subject(self, **kwargs):
        sql = "SELECT * FROM Subjects WHERE 1=1 AND "
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

    async def count_subjects(self):
        sql = "SELECT COUNT(*) FROM Subjects"
        return await self.execute(sql, fetchval=True)
    
    async def delete_subject_by_id(self, subject_id):
        sql = "DELETE FROM Subjects WHERE Id = $1"
        await self.execute(sql, subject_id, execute=True)
