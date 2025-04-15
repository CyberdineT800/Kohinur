from utils.db.postgres import Database

class Tests(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Tests (
            Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            SubjectId BIGINT,
            QuestionTxt TEXT,
            QuestionPhotoId TEXT,
            Answers JSONB,
            TestFileId INT,
            CorrectAnswerIndex INT
        );
        """
        await self.execute(sql, execute=True)

    async def add_test(self, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"${i}" for i in range(1, len(data) + 1))
        sql = f"INSERT INTO Tests ({columns}) VALUES ({placeholders}) RETURNING *"
        return await self.execute(sql, *data.values(), fetchrow=True)

    async def update_test(self, data):
        sql = """
        UPDATE Tests
        SET  
            SubjectId = $2,
            QuestionTxt = $3, 
            QuestionPhotoId = $4,
            Answers = $5,
            TestFileId = $6,
            CorrectAnswerIndex = $7
        WHERE Id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['id'],
                                  data['subjectid'],
                                  data['questiontxt'],
                                  data['questionphotoid'],
                                  data['answers'],
                                  data['testfileid'],
                                  data['correctanswerindex'],
                                  fetchrow=True)

    async def select_all_tests(self):
        sql = "SELECT * FROM Tests"
        return await self.execute(sql, fetch=True)

    async def select_test(self, **kwargs):
        sql = "SELECT * FROM Tests WHERE 1=1 AND "
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

    async def select_tests_by_subjectid(self, subject_id):
        sql = "SELECT * FROM Tests WHERE SubjectId = $1"
        return await self.execute(sql, subject_id, fetch=True)

    async def select_tests_by_testfileid(self, subject_id):
        sql = "SELECT * FROM Tests WHERE TestFileId = $1"
        return await self.execute(sql, subject_id, fetch=True)

    async def count_tests(self):
        sql = "SELECT COUNT(*) FROM Tests"
        return await self.execute(sql, fetchval=True)
    
    async def delete_test_by_id(self, test_id):
        sql = "DELETE FROM Tests WHERE Id = $1"
        await self.execute(sql, test_id, execute=True)
