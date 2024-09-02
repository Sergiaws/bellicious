from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from flask import Blueprint
from flask_mysqldb import MySQL
bp = Blueprint('database', __name__)
mysql = MySQL()
#function to insert an user
def insert_user(username, email, password, security):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO user (name, email, password, security) VALUES (%s, %s, %s, %s)", (username, email, password, security))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()


#function to get an user (used in the logIn)
def get_user_by_username_or_email(username_or_email):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id, name, email, password, security, date_created, confirmed, type FROM user WHERE name = %s OR email = %s", (username_or_email, username_or_email))
        user = cursor.fetchone()
        return user 
    except Exception as e:
        raise e
    finally:
        cursor.close()
#this function is used in the admin blueprint
def get_unconfirmed_users():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id, name, email, security, date_created, confirmed, type FROM user WHERE confirmed=0")
        user = cursor.fetchall()
        return user 
    except Exception as e:
        raise e
    finally:
        cursor.close()

def delete_user(user_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def confirm_user(user_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("UPDATE user SET confirmed = 1 WHERE id = %s", (user_id,))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def add_bookmark(url, title, annotation, description, user_id, tags, type):
    cursor = mysql.connection.cursor()
    try:
        cursor.callproc('add_bookmark', [url, title, annotation, description, user_id, tags, type])
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()



#get bookmark by ID (for updating bookmarks)
def get_bookmark_by_id(bookmark_id):
    cursor = mysql.connection.cursor()
    query = """
    SELECT 
        id, url, title, annotation, description, id_user
    FROM 
        bookmark
    WHERE 
        id = %s
    """
    cursor.execute(query, (bookmark_id,))
    bookmark = cursor.fetchone()
    cursor.close()
    return bookmark

#This function will be used in the index page
def get_top_10_bookmarks():
    cursor = mysql.connection.cursor()
    try:
        query = """
        SELECT
            bookmark.id AS bid,
            bookmark.url AS url,
            bookmark.title AS title,
            bookmark.description AS description,
            bookmark.annotation AS annotation,
            bookmark.date_created AS date,
            user.id as user_id,
            user.name AS user_name,
            COUNT(likes.id) AS like_count,
            GROUP_CONCAT(tag.tag SEPARATOR ',') AS tags
        FROM bookmark
        JOIN user ON bookmark.id_user = user.id
        LEFT JOIN likes ON bookmark.id = likes.id_bookmark
        LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.id_bookmark
        LEFT JOIN tag ON bookmark_tag.id_tag= tag.id
        WHERE bookmark.type = 1
        GROUP BY bookmark.id
        ORDER BY like_count DESC
        LIMIT 10;
        """
        cursor.execute(query)
        top_bookmarks = cursor.fetchall()
        for bookmark in top_bookmarks:
            bookmark['tags'] = bookmark['tags'].split(',') if bookmark['tags'] else []
        return top_bookmarks
    finally:
        cursor.close()

#function to delete a bookmark
def delete_bookmark(bookmark_id, user_id):
    cursor = mysql.connection.cursor()
    try:
        # Get bookmark by ID. We need to be sure that just the owner can delete its own bookmarks, and other people cannot do it.
        bookmark = get_bookmark_by_id(bookmark_id)
        
        if not bookmark:
            raise Exception("Bookmark not found")
        
        
        if bookmark['id_user'] != user_id:
            raise Exception("User is not the owner of this bookmark")
        
        
        cursor.execute("DELETE FROM bookmark WHERE id = %s", (bookmark_id,))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

#function to get the tags asociated with a bookmark
def get_tags_by_bookmark_id(bookmark_id):
    cursor = mysql.connection.cursor()
    try:
        query = """
        SELECT t.tag FROM tag t
        JOIN bookmark_tag bt ON t.id = bt.id_tag
        WHERE bt.id_bookmark = %s
        """
        cursor.execute(query, (bookmark_id,))
        tags = cursor.fetchall()
        return tags
    except Exception as e:
        raise e
    finally:
        cursor.close()


def update_bookmark(bookmark_id, title, annotation, description, bookmark_type, user_id, tags):
    cursor = mysql.connection.cursor()
    try:
        query = """
        UPDATE bookmark
        SET title = %s, annotation=%s, description = %s, type = %s
        WHERE id = %s AND id_user = %s
        """
        cursor.execute(query, (title, annotation, description, bookmark_type, bookmark_id, user_id))
        
        # Handle tags
        cursor.execute("DELETE FROM bookmark_tag WHERE id_bookmark = %s", (bookmark_id,))
        tag_list = [tag.strip() for tag in tags.split(',')]
        for tag_name in tag_list:
            cursor.execute("SELECT id FROM tag WHERE tag = %s", (tag_name,))
            tag_id = cursor.fetchone()
            if tag_id is None:
                cursor.execute("INSERT INTO tag (tag) VALUES (%s)", (tag_name,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_id['id']
            cursor.execute("INSERT INTO bookmark_tag (id_bookmark, id_tag) VALUES (%s, %s)", (bookmark_id, tag_id))
        
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def get_user_bookmarks(owner_id, viewer_id=None):
    cursor = mysql.connection.cursor()
    try:
        if viewer_id == owner_id:
            query = """
            SELECT
                bookmark.id AS bid,
                bookmark.url AS url,
                bookmark.title AS title,
                bookmark.description AS description,
                bookmark.annotation AS annotation,
                bookmark.date_created AS date,
                bookmark.type AS type,
                COUNT(likes.id) AS like_count,
                GROUP_CONCAT(tag.tag SEPARATOR ',') AS tags,
                user.name as user_name,
                user.id as user_id
            FROM bookmark
            LEFT JOIN likes ON bookmark.id = likes.id_bookmark
            LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.id_bookmark
            LEFT JOIN tag ON bookmark_tag.id_tag = tag.id
            LEFT JOIN user ON bookmark.id_user = user.id
            WHERE bookmark.id_user = %s
            GROUP BY bookmark.id
            ORDER BY bookmark.date_created DESC
            """
            cursor.execute(query, (owner_id,))
        else:
            query = """
            SELECT
                bookmark.id AS bid,
                bookmark.url AS url,
                bookmark.title AS title,
                bookmark.description AS description,
                bookmark.annotation AS annotation,
                bookmark.date_created AS date,
                bookmark.type AS type,
                COUNT(likes.id) AS like_count,
                GROUP_CONCAT(tag.tag SEPARATOR ',') AS tags,
                user.name AS user_name,
                user.id AS user_id
            FROM bookmark
            LEFT JOIN likes ON bookmark.id = likes.id_bookmark
            LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.id_bookmark
            LEFT JOIN tag ON bookmark_tag.id_tag = tag.id
            LEFT JOIN user ON bookmark.id_user = user.id
            WHERE bookmark.id_user = %s AND bookmark.type = 1
            GROUP BY bookmark.id
            ORDER BY bookmark.date_created DESC
            """
            cursor.execute(query, (owner_id,))
        bookmarks = cursor.fetchall()
        for bookmark in bookmarks:
            bookmark['tags'] = bookmark['tags'].split(',') if bookmark['tags'] else []
        return bookmarks
    finally:
        cursor.close()

def get_public_bookmarks_by_tag(tag_name):
    cursor = mysql.connection.cursor()
    try:
        query = """
        SELECT
            bookmark.id AS bid,
            bookmark.url AS url,
            bookmark.title AS title,
            bookmark.description AS description,
            bookmark.annotation AS annotation,
            bookmark.date_created AS date,
            user.id as user_id,
            user.name AS user_name,
            COUNT(likes.id) AS like_count,
            GROUP_CONCAT(tag.tag SEPARATOR ',') AS tags
        FROM bookmark
        JOIN user ON bookmark.id_user = user.id
        LEFT JOIN likes ON bookmark.id = likes.id_bookmark
        LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.id_bookmark
        LEFT JOIN tag ON bookmark_tag.id_tag = tag.id
        WHERE tag.tag = %s AND bookmark.type = 1
        GROUP BY bookmark.id
        ORDER BY like_count DESC;
        """
        cursor.execute(query, (tag_name,))
        bookmarks = cursor.fetchall()
        for bookmark in bookmarks:
            bookmark['tags'] = bookmark['tags'].split(',') if bookmark['tags'] else []
        return bookmarks
    finally:
        cursor.close()

def get_liked_bookmarks(user_id):
    cursor = mysql.connection.cursor()
    try:
        query = """
        SELECT
            bookmark.id AS bid,
            bookmark.url AS url,
            bookmark.title AS title,
            bookmark.description AS description,
            bookmark.annotation AS annotation,
            bookmark.date_created AS date,
            user.name AS user_name,
            COUNT(likes.id) AS like_count,
            GROUP_CONCAT(tag.tag SEPARATOR ',') AS tags
        FROM bookmark
        JOIN user ON bookmark.id_user = user.id
        JOIN likes ON bookmark.id = likes.id_bookmark
        LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.id_bookmark
        LEFT JOIN tag ON bookmark_tag.id_tag = tag.id
        WHERE likes.id_user = %s
        GROUP BY bookmark.id
        ORDER BY bookmark.date_created DESC;
        """
        cursor.execute(query, (user_id,))
        liked_bookmarks = cursor.fetchall()
        for bookmark in liked_bookmarks:
            bookmark['tags'] = bookmark['tags'].split(',') if bookmark['tags'] else []
        return liked_bookmarks
    finally:
        cursor.close()

def like_bookmark(user_id, bookmark_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id FROM likes WHERE id_user = %s AND id_bookmark = %s", (user_id, bookmark_id))
        result = cursor.fetchone()
        
        if result:
            raise ValueError('User has already liked this bookmark')

        cursor.execute("INSERT INTO likes (id_user, id_bookmark) VALUES (%s, %s)", (user_id, bookmark_id))
        cursor.execute("UPDATE bookmark SET likes = likes + 1 WHERE id = %s", (bookmark_id,))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

#import bookmarks using html
def import_bookmarks_html(html_content, user_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    cursor = mysql.connection.cursor()
    
    try:
        for a in soup.find_all('a'):
            url = a.get('href')
            title = a.text
            tags = a.get('tags', '')
            annotation = ''
            description = ''

            cursor.callproc('add_bookmark', [url, title, annotation, description, user_id, tags])
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def import_bookmarks_xml(xml_content, user_id):
    root = ET.fromstring(xml_content)
    cursor = mysql.connection.cursor()
    
    try:
        for post in root.findall('post'):
            url = post.get('href')
            title = post.get('description')
            tags = post.get('tag', '').replace(" ", ",")
            annotation = post.get('extended', '')
            description = ''

            cursor.callproc('add_bookmark', [url, title, annotation, description, user_id, tags])
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def export_bookmarks_html(user_id):
    cursor = mysql.connection.cursor()
    try:
        query = """
        SELECT bookmark.url, bookmark.title, bookmark.description, bookmark.annotation, UNIX_TIMESTAMP(bookmark.date_created) as add_date, 0 as private, GROUP_CONCAT(tag.name) as tags
        FROM bookmark
        LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.bookmark_id
        LEFT JOIN tag ON bookmark_tag.tag_id = tag.id
        WHERE bookmark.id_user = %s
        GROUP BY bookmark.id
        """
        cursor.execute(query, (user_id,))
        bookmarks = cursor.fetchall()
        
        html_content = '<!DOCTYPE netscape-bookmark-file-1><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>Bookmarks</title></head><body><h1>Bookmarks</h1><dl><p>'
        for bm in bookmarks:
            tags = bm['tags'] if bm['tags'] else ''
            html_content += f'<dt><a href="{bm["url"]}" add_date="{bm["add_date"]}" private="{bm["private"]}" tags="{tags}">{bm["title"]}</a></dt>'
        html_content += '</dl></body></html>'
        return html_content
    finally:
        cursor.close()

def export_bookmarks_xml(user_id):
    cursor = mysql.connection.cursor()
    try:
        query = """
        SELECT bookmark.url, bookmark.title, bookmark.description, bookmark.annotation, bookmark.date_created, GROUP_CONCAT(tag.name) as tags
        FROM bookmark
        LEFT JOIN bookmark_tag ON bookmark.id = bookmark_tag.bookmark_id
        LEFT JOIN tag ON bookmark_tag.tag_id = tag.id
        WHERE bookmark.id_user = %s
        GROUP BY bookmark.id
        """
        cursor.execute(query, (user_id,))
        bookmarks = cursor.fetchall()

        root = ET.Element('posts', user="username", total=str(len(bookmarks)))
        for bm in bookmarks:
            tags = bm['tags'] if bm['tags'] else ''
            ET.SubElement(root, 'post', href=bm['url'], description=bm['title'], extended=bm['annotation'], time=bm['date_created'].isoformat(), tag=tags)

        xml_content = ET.tostring(root, encoding='utf8').decode('utf8')
        return xml_content
    finally:
        cursor.close()

#function to change the privacy of the bookmarks (for administrators)
def change_bookmark_privacy(bookmark_id):
    cursor = mysql.connection.cursor()
    try:
        query = "UPDATE bookmark SET type = IF(type=1, 0, 1) WHERE id = %s"
        cursor.execute(query, (bookmark_id,))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def get_top_10_tags():
    cursor = mysql.connection.cursor()
    query = """
    SELECT tag.tag, COUNT(bookmark_tag.id_bookmark) AS bookmark_count
    FROM tag
    LEFT JOIN bookmark_tag ON tag.id = bookmark_tag.id_tag
    LEFT JOIN bookmark ON bookmark_tag.id_bookmark = bookmark.id
    WHERE tag.tag IS NOT NULL AND tag.tag != '' AND bookmark.type = 1
    GROUP BY tag.tag
    ORDER BY bookmark_count DESC
    LIMIT 10
    """
    try:
        cursor.execute(query)
        top_tags = cursor.fetchall()
        return top_tags
    except Exception as e:
        raise e
    finally:
        cursor.close()
