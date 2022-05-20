import GeneralCommands as GC
from github import Github

path = 'C:\\Users\\Darryn\\Desktop\\Code\\DATA LOGGER PI\\Raspberry Pi\\'
def uploadGithub(path):
    
    #######################################################################
    #Try to write last 50 data points to online log
    
    try:
        csvFile = []
        header = []
        with open(path+'AllTempLogs.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                csvFile.append(row)

        header = csvFile[0]
        csvFile = csvFile[-50:]
        
        with open(path+'OnlineLog.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in csvFile:
                writer.writerow(row)
    except Exception as err:
        return 'ERROR: ' + str(err)
    
    #######################################################################
    #Try to connect to Github
    
    try: 
        token = GC.get_settings('Github', path)
        g = Github(token) #token key
        
        repo = g.get_user().get_repo("View") #Repository
        all_files = []
        contents = repo.get_contents("")
        print(repo)
    except Exception as err:
        return "ERROR: " + str(err)

    #######################################################################
    #Try to upload the file to Github
    
    try:
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
    
        with open(path + 'OnlineLog.csv', 'r') as file: #file to open
            content = file.read()
    
        #Upload to Github
        git_file = 'OnlineLog.csv'
        if git_file in all_files:
            contents = repo.get_contents(git_file)
            repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
            print(git_file + ' UPDATED')
        else:
            repo.create_file(git_file, "committing files", content, branch="master")
            print(git_file + ' CREATED')
            
        return 'Uploaded to Github'
        
    except Exception as err:
        return 'ERROR: ' + str(err)
