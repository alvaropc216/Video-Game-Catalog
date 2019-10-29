# Video Game Catalog

## About

This project present a Video Game catalog that allows the creation and deletion of genres (game categories) and individual games within each genre. Each game has a title and a description which can be edited or deleted. Genres can be deleted only. When a Genre is deleted, all games within will also be deleted. The catalog also includes a username functionality where only users who have created a genre / game can edit or delete said genre / game.

## Prerequisites

### Virtualbox and Vagrant

The program executes within a Virtual Machine (VirtualBox). VirtualBox can be downloaded from:
```
https://www.virtualbox.org/wiki/downloads
```
The environment used to test the program is Vagrant. Vagrant can be downloaded from:
```
https://www.vagrantup.com/downloads.html
```
### Fullstack Nanodegree VM

After installing Virtualbox and Vagrant, the program will also require the use of the Udacity fullstack-nanodegree-vm.
```
http://github.com/udacity/fullstack-nanodegree-vm
```
After downloading the fullstack-nonodegree and once in the folder, type `vagrant up`. If the installation is successful type `vagrant ssh` to run the VM

### Video Game Catalog Packet

The Video Game Catalog packet should include the following files:

1. *videogames.py* :which runs the page
2. *database_setup.py* :which sets up the initial database
3. *fb_client_secrets.json* :which holds information to allow facebook login (oauth)
4. *templates* :which has all the templates to be rendered in the webpage

## Setup

After completing all the steps in the previous sections the following step is to set up the database. In order to do this type the following:

```
python database_setup.py
```

A successful run would create a database named `gamecatalog.db`.

## Running the Video Game catalog

Once the above steps are completed you should be able to run the main file.

```
python videogames.py
```
## Use

The video game catalog runs through the VM an uses *Port 5000*. In order to go to the main page use the following:

```
http://localhost:5000
```

Once in the main page you will have to Login in order to create a genre or create a game within a genre. The database will begin empty, so the user should provide genres and games to fill the database.

### JSON Functionality

The information in the database can be accessed using JSON.

If you want to receive the information for all Genres, use the following:
```
http://localhost:5000/main/JSON
```

If you want to receive the information for a particular Genre, showing all games from that group, use the following:

```
http://localhost:5000/main/<int:genre_id>/jSON
```
Where `<int:genre_id>` represent the unique ID that identifies the desired Genre (This ID can be seen in the first JSON request for all Genres)

Thank you for using the Video Game catalog!
