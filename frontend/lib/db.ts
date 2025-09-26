import mysql from 'mysql2/promise';

const dbConfig = {
  host: process.env.DB_HOST || 'glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com',
  user: process.env.DB_USER || 'select_admin',
  password: process.env.DB_PASSWORD || 'GR558AvfoYFz7NTZ1q8n',
  database: process.env.DB_NAME || 'cost_reporter',
  port: 3306,
};

export async function getConnection() {
  try {
    const connection = await mysql.createConnection(dbConfig);
    return connection;
  } catch (error) {
    console.error('Database connection error:', error);
    throw error;
  }
}

export async function query(sql: string, params?: any[]) {
  const connection = await getConnection();
  try {
    const [results] = await connection.execute(sql, params);
    return results;
  } finally {
    await connection.end();
  }
}
