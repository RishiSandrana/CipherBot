import requests

badge_id = 3869573452105469

listOfRMHRoleIDs = [3627780, 19516868, 25919204, 4059372, 26957538, 3927521, 3627781, 36896118, 36747671, 19962820, 3704753, 3720799, 36896024, 26492648, 4165630]

for roleID in listOfRMHRoleIDs:
    userResponse = requests.get(f'https://groups.roblox.com/v1/groups/619142/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
    for user in userResponse['data']:
        userId = user['userId']
        badgeResponse = requests.get(f'https://badges.roproxy.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
        print(badgeResponse)