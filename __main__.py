import mapper
from controller import controller
import time


def run_api(connection):
    start_time = time.time()
    print('''Securely downloading temporary CSV from 
    \'http://chargepoints.dft.gov.uk/api/retrieve/registry/format/csv\' 
     under OGL \'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/\'''')

    data = controller.get_csv()
    print('Uploading to Database...')
    controller.parse_csv(connection, data)
    connection.commit()

    print("--- %s seconds ---" % (time.time() - start_time))

    return connection


def menu():
    print('a - Update database')
    print('f - Find charge point')
    print('d - download csv to local')
    print('m - map points')
    print('q - quit')


def interface(connection):
    entry = True
    while entry:
        menu()
        value = input("Enter option:\n")

        if value == 'a':
            run_api(connection)

        elif value == 'f':

            print('Search by: ')
            print('t - town')
            print('c - county')
            print('p - postcode')

            flag = True
            while flag:
                print('Enter option: ')
                value = input()
                if value == 't':
                    town = input('Enter town\n')
                    where = 'town LIKE \'%' + town + '%\''
                    data = connection.execute(
                        'SELECT reference, name, buildingNumber, thoroughfare, street, town, county, postcode, latitude, longitude FROM registry WHERE ' + where + ';').fetchall()

                    flag = False
                elif value == 'c':
                    county = input('Enter county\n')
                    where = 'county LIKE \'%' + county + '%\''
                    data = connection.execute(
                        'SELECT reference, name, buildingNumber, thoroughfare, street, town, county, postcode, latitude, longitude FROM registry WHERE ' + where + ';').fetchall()

                    flag = False
                elif value == 'p':
                    postcode = input('Enter postcode\n')
                    where = 'postcode LIKE \'%' + postcode + '%\''
                    data = connection.execute(
                        'SELECT reference, name, buildingNumber, thoroughfare, street, town, county, postcode, latitude, longitude FROM registry WHERE ' + where + ';').fetchall()
                    flag = False

                else:
                    print('Invalid entry')

            info = []
            print('Results: ' + str(len(data)) + '\n')
            start_time = time.time()
            for point in data:
                for i in point:
                    info.append(i)
                print('Reference: ' + info[0] + '\nName: ' + info[1] + '\nBuilding Number: ' + info[
                    2] + '\nThoroughfare: ' + info[3] + '\nStreet: ' + info[4] + '\nTown: ' + info[
                          5] + '\nCounty: ' + info[6] + '\nPostcode: ' + info[7] + '\nLatitude: ' + info[
                          8] + '\nLongitude: ' + info[9] + '\n')
                info.clear()

            if len(data) == 0:
                print('No results')
            else:
                print('Results: ' + str(len(data)) + '\n')
            print("--- %s seconds ---" % (time.time() - start_time))

        elif value == 'd':
            try:
                open('out.csv')
                print('File already exists')
            except FileNotFoundError as e:
                try:
                    controller.download_csv()
                except:
                    print('Error downloading csv')
            except:
                print('Error')



        elif value == 'm':
            try:
                if connection.execute('SELECT * FROM registry;').fetchall() == []:
                    print('Database empty, updating now...')
                    run_api(connection)
                else:

                    mapper.mapper.draw_map(connection)

            except:
                connection = controller.connect_database()

                if connection.execute('SELECT * FROM registry;').fetchall() == []:
                    print('Updating database first...')
                    run_api(connection)
                else:
                    mapper.mapper.draw_map(connection)


        elif value == 'q':
            print("Exiting program")
            entry = False

        else:
            print("Invalid entry")


if __name__ == "__main__":
    print('''
//         _    _  
//    _   / _  / ) 
//   )_) (__/ (_/  
//  (_                                                                                             
                                     ''')
    print('''eGo | alpha - Electric Charge Point Mapper and Database Generator
    This programme makes use of the UK GOV database on electric charge points and their locations.
    You can update the database, do a manual search and generate a folium based map.
    This version uses the sqlite database package to create a virtual database within python.
    Other work-in-progress versions use MySQL server databases to retrieve and store data.
    This programme will eventually be used to build geospatial visual analytics for use within the sector.\n''')

    connection = controller.connect_database()
    interface(connection)
