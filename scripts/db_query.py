#!/usr/bin/env python3
"""
Database query module for pulling ezlrounds data from SQL Server.
"""

import pyodbc
import csv
from datetime import datetime
from typing import List, Dict, Optional


class EZLinksRoundsDB:
    """Query SQL Server database for ezlrounds data."""

    def __init__(self, server: str, database: str, username: Optional[str] = None,
                 password: Optional[str] = None, use_windows_auth: bool = True):
        """
        Initialize database connection.

        Args:
            server: SQL Server hostname or IP
            database: Database name
            username: Username (if using SQL auth)
            password: Password (if using SQL auth)
            use_windows_auth: Use Windows authentication (default True)
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.use_windows_auth = use_windows_auth
        self.connection = None

    def connect(self):
        """Establish database connection."""
        if self.use_windows_auth:
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
            )

        try:
            self.connection = pyodbc.connect(conn_str)
            print(f"Connected to {self.database} on {self.server}")
            return True
        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Disconnected from database")

    def query_rounds_data(self, table_name: str, date_column: str = "playdatekey",
                         count_column: str = "count", start_date: Optional[str] = None,
                         end_date: Optional[str] = None, base_query: Optional[str] = None,
                         filtered_query: Optional[str] = None, order_by: Optional[str] = None) -> List[Dict]:
        """
        Query rounds data from the database.

        Args:
            table_name: Name of the table to query
            date_column: Name of the date column (default: playdatekey)
            count_column: Name of the count column (default: count)
            start_date: Optional start date filter (YYYYMMDD format)
            end_date: Optional end date filter (YYYYMMDD format)
            base_query: Optional custom SQL query template (from config)
            filtered_query: Optional custom SQL query with WHERE clause (from config)
            order_by: Optional ORDER BY clause (from config)

        Returns:
            List of dictionaries with playdatekey and count
        """
        if not self.connection:
            if not self.connect():
                return []

        # Build WHERE clause if dates provided
        where_clauses = []
        if start_date:
            where_clauses.append(f"{date_column} >= '{start_date}'")
        if end_date:
            where_clauses.append(f"{date_column} <= '{end_date}'")

        # Build query
        if where_clauses and filtered_query:
            # Use custom filtered query from config
            where_clause = " AND ".join(where_clauses)
            query = filtered_query.format(
                date_column=date_column,
                count_column=count_column,
                table=table_name,
                where_clause=where_clause
            )
        elif base_query:
            # Use custom base query from config
            query = base_query.format(
                date_column=date_column,
                count_column=count_column,
                table=table_name
            )
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        else:
            # Default query
            query = f"SELECT {date_column}, {count_column} FROM {table_name}"
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        # Add ORDER BY clause
        if order_by:
            query += " " + order_by.format(date_column=date_column)
        else:
            query += f" ORDER BY {date_column}"

        print(f"Executing query: {query}")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            results = []
            for row in cursor:
                results.append({
                    'playdatekey': str(row[0]),
                    'count': int(row[1])
                })

            print(f"Retrieved {len(results)} records")
            return results

        except pyodbc.Error as e:
            print(f"Error executing query: {e}")
            return []

    def get_latest_date(self, table_name: str, date_column: str = "playdatekey",
                       max_date_query: Optional[str] = None) -> Optional[str]:
        """
        Get the latest date in the database.

        Args:
            table_name: Name of the table to query
            date_column: Name of the date column
            max_date_query: Optional custom SQL query template (from config)

        Returns:
            Latest date as string (YYYYMMDD format) or None
        """
        if not self.connection:
            if not self.connect():
                return None

        if max_date_query:
            query = max_date_query.format(date_column=date_column, table=table_name)
        else:
            query = f"SELECT MAX({date_column}) FROM {table_name}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()

            if result and result[0]:
                return str(result[0])
            return None

        except pyodbc.Error as e:
            print(f"Error getting latest date: {e}")
            return None

    def export_to_csv(self, data: List[Dict], output_file: str = "ezlrounds.csv"):
        """
        Export data to CSV file.

        Args:
            data: List of dictionaries with playdatekey and count
            output_file: Output CSV filename
        """
        if not data:
            print("No data to export")
            return

        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['playdatekey', 'count'])
                writer.writeheader()
                writer.writerows(data)

            print(f"Exported {len(data)} records to {output_file}")

        except IOError as e:
            print(f"Error writing to file: {e}")

    def update_csv(self, table_name: str, csv_file: str = "ezlrounds.csv",
                   date_column: str = "playdatekey", count_column: str = "count",
                   base_query: Optional[str] = None, filtered_query: Optional[str] = None,
                   order_by: Optional[str] = None, max_date_query: Optional[str] = None,
                   force_start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Update CSV file with new data from database.

        Args:
            table_name: Name of the table to query
            csv_file: CSV file to update
            date_column: Name of the date column
            count_column: Name of the count column
            base_query: Optional custom SQL query template (from config)
            filtered_query: Optional custom SQL query with WHERE clause (from config)
            order_by: Optional ORDER BY clause (from config)
            max_date_query: Optional custom MAX query (from config)
            force_start_date: Optional forced start date (overrides CSV date)
            end_date: Optional end date filter
        """
        # Read existing CSV to find latest date
        latest_csv_date = None
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    latest_csv_date = row['playdatekey']
            print(f"Latest date in CSV: {latest_csv_date}")
        except FileNotFoundError:
            print(f"CSV file not found, will create new file")

        # Determine start date to use
        if force_start_date:
            start_date = force_start_date
            print(f"Using forced start date: {start_date}")
        elif latest_csv_date:
            start_date = latest_csv_date
        else:
            start_date = None

        # Query database for new data
        if start_date:
            # Get data after the start date
            data = self.query_rounds_data(
                table_name, date_column, count_column,
                start_date=start_date,
                end_date=end_date,
                base_query=base_query,
                filtered_query=filtered_query,
                order_by=order_by
            )
            # Remove the duplicate date if it exists (only if not forced)
            if not force_start_date and data and data[0]['playdatekey'] == start_date:
                data = data[1:]
        else:
            # Get all data
            data = self.query_rounds_data(
                table_name, date_column, count_column,
                end_date=end_date,
                base_query=base_query,
                filtered_query=filtered_query,
                order_by=order_by
            )

        if not data:
            print("No new data to update")
            return

        # Append to existing CSV or create new
        try:
            if latest_csv_date and not force_start_date:
                # Append mode
                with open(csv_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['playdatekey', 'count'])
                    writer.writerows(data)
                print(f"Appended {len(data)} new records to {csv_file}")
            else:
                # Create new file
                self.export_to_csv(data, csv_file)

        except IOError as e:
            print(f"Error updating CSV file: {e}")

    def refresh_full_csv(self, table_name: str, csv_file: str = "ezlrounds.csv",
                        date_column: str = "playdatekey", count_column: str = "count",
                        base_query: Optional[str] = None, filtered_query: Optional[str] = None,
                        order_by: Optional[str] = None,
                        start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Refresh the entire CSV file with all data from database.

        Args:
            table_name: Name of the table to query
            csv_file: CSV file to create/overwrite
            date_column: Name of the date column
            count_column: Name of the count column
            base_query: Optional custom SQL query template (from config)
            filtered_query: Optional custom SQL query with WHERE clause (from config)
            order_by: Optional ORDER BY clause (from config)
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        print("Refreshing full CSV from database...")
        data = self.query_rounds_data(
            table_name, date_column, count_column,
            start_date=start_date,
            end_date=end_date,
            base_query=base_query,
            filtered_query=filtered_query,
            order_by=order_by
        )
        if data:
            self.export_to_csv(data, csv_file)


def main():
    """Example usage."""
    # TODO: Update these connection details
    SERVER = "your-server-name"
    DATABASE = "your-database-name"
    TABLE = "your-table-name"

    # Option 1: Windows Authentication
    db = EZLinksRoundsDB(SERVER, DATABASE, use_windows_auth=True)

    # Option 2: SQL Server Authentication
    # db = EZLinksRoundsDB(SERVER, DATABASE, username="your-username",
    #                      password="your-password", use_windows_auth=False)

    try:
        # Connect to database
        if db.connect():

            # Get latest date in database
            latest_date = db.get_latest_date(TABLE)
            print(f"Latest date in database: {latest_date}")

            # Update CSV with new data
            db.update_csv(TABLE)

            # Or refresh entire CSV
            # db.refresh_full_csv(TABLE)

    finally:
        # Always disconnect
        db.disconnect()


if __name__ == '__main__':
    main()
