import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import requests
import sys

USEREPLAYID = False
PRINTTIMELINE = False
PERIOD_NO = 2

# 고정 스펙
dR = 826.5 # 데미지, 보스 데미지, 상추뎀
madR = 144
mobpdpR = 3.8 * 0.0102 # 98.98%
criticalDamage = 165.15
bufftimeR = 71
summonTimeR = 40

dR += 4 # 와헌 유니온
mobpdpR *= 0.91 # 모법 링크

dR = 100 + dR
madR = 100 + madR
cdR = 135 + criticalDamage

base_multiplier = dR * madR * cdR * (1 - mobpdpR)

# 0 정뿌, 1 강분출, 2 바람분출, 3 해분출, 4 장판, 5 화산탄,
# 6 씨앗, 7 잠깨, 8 강흡수, 9 바람흡수, 10 해흡수, 11 넝쿨타래,
# 12 큰기지개, 13 해강산1타, 14 해강산2타, 15 용솟음, 16 산등성이,
# 17 스인미 1타, 18 스인미 2타, 19 크오솔 1타, 20 크오솔 2타,
# 21 꽃누리1타, 22 꽃누리2타,
# 23 헤카테, 24 스틱스1타, 25 스틱스2타, 26 스틱스3타, 27 플레게톤1타, 28 플레게톤2타, 29 화중군자
# 솔 헤카테 : 플레게톤은 해 강 산 바람에 감응시킨다.

damage = [4821, 10396.575, 4190.508, 3825.36, 1025.892, 9598.176,
          1369, 21160, 5385.105, 901.692, 5142.984, 2802,
          174960, 11200, 246600/11, 10880, 3200,
          152500/11, 854000/297, 1830500/99, 30500/9,
          73500/11, 96950/11,
          2400, 78280/11, 29080/11, 8960, 1700, 36240/11, 1121750 / 891]

dRS = [0, 25 + summonTimeR / 2, 25 + summonTimeR / 2, 25 + summonTimeR / 2, 25 + summonTimeR / 2, 25 + summonTimeR / 2,
       60, 0, 25, 25, 25, 0,
       0, 0, 0, 0, 0,
       0, 0, 0, 0,
       50, 50,
       40, 40, 40, 40, 40, 40, 0]
mobpdpRS = [0.8, 0.68, 0.68, 0.68, 0.68, 0.68,
            0.8, 0.8, 0.68, 0.68, 0.68, 0.8,
            1, 1, 1, 1, 1,
            1, 1, 1, 1,
            0.5, 0.5,
            0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1]

# get file
headers = {
    "x-nxopen-api-key": "asdf"
}

f = open("api_key.txt", 'r')
headers['x-nxopen-api-key'] = f.read()
f.close()
print("API key:", headers['x-nxopen-api-key'])

export = open('result.csv', 'w', newline = '')
wr = csv.writer(export)
export2 = open('detail.csv', 'w', newline = '')
wr2 = csv.writer(export2)

if PRINTTIMELINE:
    exportTL = open('timeline.csv', 'w', newline = '')
    wrTL = csv.writer(exportTL)
    skillstr = ['정뿌', '강분출', '바람분출', '해분출', '장판', '화산탄',
                '씨앗', '잠깨', '강흡수', '바람흡수', '해흡수', '넝쿨타래',
                '큰기지개', '해강산', '해강산2', '용솟음', '산등성이',
                '스인미1', '스인미2', '크오솔1', '크오솔2',
                '꽃누리1', '꽃누리2',
                '헤카테', '스틱스1', '스틱스2', '스틱스3', '플레게톤1', '플레게톤2', '화중군자']
    wrTL.writerow(['스킬', '시각'])

res = [0, '닉네임', 'OCID', '리플레이 ID', '리레', '쿨감', '시간', '점수', '유효']
detail = [0, '닉네임', '정뿌', '강분출', '바람분출', '해분출',
          '씨앗', '잠깨', '강흡수', '바람흡수', '해흡수', '넝쿨타래',
          '큰기지개', '해강산', '용솟음', '산등성이', '스인미', '크오솔',
          '꽃누리', '헤카테', '스틱스', '플레게톤', '화중군자']
indetail = [2, 3, 4, 5, 5, 5,
            6, 7, 8, 9, 10, 11,
            12, 13, 13, 14, 15,
            16, 16, 17, 17,
            18, 18,
            19, 20, 20, 20, 21, 21, 22]

if USEREPLAYID:
    ocids = []
    with open('ocid.txt', encoding = 'UTF-8') as file:
        while line := file.readline():
            ocids.append(line.rstrip())
    replays = []
    with open('replay_id.txt', encoding = 'UTF-8') as file:
        while line := file.readline():
            replays.append(line.rstrip())

with open('nickname.txt', encoding = 'UTF-8') as file:
    while line := file.readline():
        wr.writerow(res)
        wr2.writerow(detail)
        if USEREPLAYID:
            ocid = ocids[res[0]]
            replay_id = replays[res[0]]
        res[0] += 1
        detail[0] += 1
        for i in range(1, 9):
            res[i] = ''
        for i in range(1, 23):
            detail[i] = 0
        res[1] = detail[1] = characterName = line.rstrip()
        
        if not USEREPLAYID:
            urlString = "https://open.api.nexon.com/maplestory/v1/id?character_name=" + characterName
            response = requests.get(urlString, headers = headers)

            if 'ocid' not in response.json():
                print("ERROR:", characterName, "의 OCID가 존재하지 않습니다.")
                continue
            ocid = response.json()['ocid']
        res[2] = ocid

        if not USEREPLAYID:
            urlString = "https://open.api.nexon.com/maplestory/v1/battle-practice/replay-id?ocid=" + ocid
            response = requests.get(urlString, headers = headers)
            
            if 'replay_list' not in response.json():
                print("ERROR:", characterName, "의 리플레이가 존재하지 않습니다.")
                continue
            replay_id = None
            for rl in response.json()['replay_list']:
                if rl['period_no'] == PERIOD_NO:
                    replay_id = rl['replay_id']
                    break
            if replay_id == None:
                print("ERROR:", characterName, "의 리플레이가 존재하지 않습니다.")
                continue
        res[3] = replay_id

        urlString = "https://open.api.nexon.com/maplestory/v1/battle-practice/character-info?replay_id=" + replay_id
        response = requests.get(urlString, headers = headers)
        
        if 'stat_object' not in response.json():
            print("ERROR:", characterName, "의 캐릭터 정보를 불러올 수 없습니다.")
            continue
        res[8] = True
        
        character_info = response.json()
        stat = character_info['stat_object']['basic_stat_object']['final_stat']
        #criticaldamage = stat[7]['stat_value']
        #bufftimeR = stat[30]['stat_value']
        coolTime = int(stat[33]['stat_value'])
        #diseaseDamR = stat[37]['stat_value']
        #summonTimeR = stat[43]['stat_value']
        skill = character_info['skill_object']['character_skill']
        restraint = 0
        #continuous = 0
        for sk in skill:
            if sk['skill_name'] == '리스트레인트 링':
                restraint = sk['skill_level']
            #if sk['skill_name'] == '컨티뉴어스 링':
                #continuous = sk['skill_level']
        res[4] = restraint
        res[5] = coolTime
        
        urlString = "https://open.api.nexon.com/maplestory/v1/battle-practice/skill-timeline?replay_id=" + replay_id
        response = requests.get(urlString, headers = headers)
        
        if 'skill_timeline' not in response.json():
            print("ERROR:", characterName, "의 스킬 내역을 불러올 수 없습니다.")
            continue
        
        timeline = response.json()['skill_timeline']
        
        # 버프 스킬
        dRA = [0 for x in range(400000)]
        madRA = [0 for x in range(400000)]
        mobpdpRA = [1 for x in range(400000)]
        cdRA = [0 for x in range(400000)]
        mdRA = [1 for x in range(400000)]

        start = 0
        for sk in timeline:
            if start == 0 and sk['sequence_name'] != None:
                start = sk['elapse_time']
                break
        end = start + 338400 - 1000 * coolTime
        skillRemain = [6, 6, 3, 3, 3, 6, 6, 6] # 엔버, 너울가지, 아름드리, 그여축, 리레, 큰기지개, 산등성이, 스틱스
        skillCooltime = [56400, 56400, 112800, 112800, 112800]
        for i in range(5):
            skillCooltime[i] -= coolTime * 1000

        for sk in timeline:
            sequence = -1
            if sk['skill_name'] == '소울 컨트랙트':
                sequence = 0
            elif sk['skill_name'] == '너울가지':
                sequence = 1
            elif sk['skill_name'] == '아름드리 나무':
                sequence = 2
            elif sk['skill_name'] == '그란디스 여신의 축복':
                sequence = 3
            elif sk['skill_name'] == '리스트레인트 링':
                sequence = 4
            if sequence >= 0:
                if skillRemain[sequence] == 0:
                    continue
                skillRemain[sequence] -= 1
                end = max(end, sk['elapse_time'] + skillCooltime[sequence])
                time = sk['elapse_time']
                if sequence == 0:
                    for t in range(100 * (100 + bufftimeR)):
                        dRA[time + t] += 60
                elif sequence == 1:
                    for t in range(20000):
                        mdRA[time + t] *= 1.09
                elif sequence == 2:
                    for t in range(20000):
                        dRA[time + t] += 30
                        cdRA[time + t] = 10 # unique
                        mobpdpRA[time + t] = 0.85 # unique
                elif sequence == 3:
                    for t in range(40000):
                        dRA[time + t] += 40
                        mdRA[time + t] *= 1.11 / 1.05
                elif sequence == 4:
                    for t in range((restraint > 4) * 20000 + (restraint < 5) * (restraint * 2000 + 7000)):
                        madRA[time + t] = 17 * (restraint - (restraint > 4)) # unique
            elif sk['skill_name'] == '안다미로':
                end = max(end, sk['elapse_time'] + 2280)
                start = min(start, sk['elapse_time'])
        elapsed = end - start
        res[6] = format(elapsed / 1000, ".3f")
        print("닉네임:", characterName)
        print("측정:", start, "-", end)

        # 0 정뿌, 1 강분출, 2 바람분출, 3 해분출, 4 장판, 5 화산탄,
        # 6 씨앗, 7 잠깨, 8 강흡수, 9 바람흡수, 10 해흡수, 11 넝쿨타래,
        # 12 큰기지개, 13 해강산1타, 14 해강산2타, 15 용솟음, 16 산등성이,
        # 17 스인미 1타, 18 스인미 2타, 19 크오솔 1타, 20 크오솔 2타,
        # 21 꽃누리1타, 22 꽃누리2타,
        # 23 헤카테, 24 스틱스1타, 25 스틱스2타, 26 스틱스3타, 27 플레게톤1타, 28 플레게톤2타
        # 솔 헤카테 : 플레게톤은 해 강 산 바람에 감응시킨다.
        
        damageSkill = []
        ascent = []
        
        # 솔 헤카테 추가
        Hekate = [True, False, False, True, False, False,
                  False, True, False, False, False, True,
                  True, True, True, True, True,
                  True, False, True, False,
                  True, True,
                  False, True, False, False, False, False, False]
        HekateUntil = -1
        HekateSince = 0
        
        absorption = 0
        eruption = [999999, 999999, 999999] # 강, 바람, 해
        mountainSeed = [-28000, -28000, -28000] # 산의 씨앗을 설치한 시각
        mountainSeedRefill = 0 # 산의 씨앗이 완충되는 시점
        mountainSeedTurn = 0
        
        for sk in timeline:
            skillName = sk['skill_name']
            time = sk['elapse_time']
            if HekateUntil >= time:
                while HekateSince < time:
                    damageSkill.append((23, HekateSince + 450))
                    HekateSince += 3500
            if skillName == '정기 뿌리기 VI':
                damageSkill.append((0, time))
                if time >= absorption:
                    absorption = time + 4700
                    damageSkill.append((8, time))
                    for i in range(6):
                        damageSkill.append((9, time + i * 30))
                    damageSkill.append((10, time + 1080))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '분출 : 너울이는 강 VI':
                for i in range(15):
                    if eruption[0] + 1800 + i * 1800 >= time:
                        break
                    damageSkill.append((1, eruption[0] + 1800 + i * 1800))
                eruption[0] = time
                if mountainSeedRefill <= time + 20000:
                    mountainSeedRefill = max(mountainSeedRefill, time) + 10000
                    for i in range(14):
                        if mountainSeed[mountainSeedTurn] + 990 + i * 2000 >= time:
                            break
                        damageSkill.append((6, mountainSeed[mountainSeedTurn] + 990 + i * 2000))
                    mountainSeed[mountainSeedTurn] = time
                    if mountainSeedTurn == 2:
                        mountainSeedTurn = 0
                    else:
                        mountainSeedTurn += 1
            elif skillName == '분출 : 돌개바람 VI':
                for i in range(10):
                    if eruption[1] + 1800 + i * 3000 >= time:
                        break
                    for j in range(4):
                        damageSkill.append((2, eruption[1] + 1800 + i * 3000 + 480 + j * 480))
                eruption[1] = time
                if mountainSeedRefill <= time + 20000:
                    mountainSeedRefill = max(mountainSeedRefill, time) + 10000
                    for i in range(14):
                        if mountainSeed[mountainSeedTurn] + 990 + i * 2000 >= time:
                            break
                        damageSkill.append((6, mountainSeed[mountainSeedTurn] + 990 + i * 2000))
                    mountainSeed[mountainSeedTurn] = time
                    if mountainSeedTurn == 2:
                        mountainSeedTurn = 0
                    else:
                        mountainSeedTurn += 1
            elif skillName == '분출 : 해돋이 우물 VI':
                damageSkill.append((3, eruption[2]))
                for i in range(29):
                    if eruption[2] + 2000 + i * 1000 >= time:
                        break
                    damageSkill.append((4, eruption[2] + 2000 + i * 1000))
                for i in range(13):
                    if eruption[2] + 2100 + i * 2100 >= time:
                        break
                    damageSkill.append((5, eruption[2] + 2100 + i * 2100 + 750))
                eruption[2] = time
                if mountainSeedRefill <= time + 20000:
                    mountainSeedRefill = max(mountainSeedRefill, time) + 10000
                    for i in range(14):
                        if mountainSeed[mountainSeedTurn] + 990 + i * 2000 >= time:
                            break
                        damageSkill.append((6, mountainSeed[mountainSeedTurn] + 990 + i * 2000))
                    mountainSeed[mountainSeedTurn] = time
                    if mountainSeedTurn == 2:
                        mountainSeedTurn = 0
                    else:
                        mountainSeedTurn += 1
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '잠 깨우기 VI':
                damageSkill.append((7, time + 1140))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '넝쿨 타래':
                damageSkill.append((11, time))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '큰 기지개':
                skillRemain[5] -= 1
                if skillRemain[5] < 0:
                    continue # 6회 제한 적용
                damageSkill.append((12, time + 1320))
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '해 강 산 바람':
                for t in [1260, 1260, 1260, 1590, 1620, 1650, 2280, 2310, 2340, 3180, 3210, 3240]:
                    damageSkill.append((13, time + t))
                for i in range(7):
                    damageSkill.append((14, time + 5880 + i * 30))
                for t in [960, 1800, 1980, 2160, 2340, 2520, 2700, 2880]:
                    damageSkill.append((27, time + t)) # 솔 헤카테 : 플레게톤
                for i in range(10):
                    damageSkill.append((28, time + 3480 + i * 60))
                HekateSince = max(HekateSince, time + 4200)
                HekateUntil = max(HekateUntil, time + 5000 + 3240)
            elif skillName == '용솟음치는 정기':
                for t in [180, 360, 1260, 1380, 1500, 1620]:
                    damageSkill.append((15, time + t))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '산등성이 굽이굽이':
                skillRemain[6] -= 1
                if skillRemain[6] < 0:
                    continue # 6회 제한 적용
                for i in range(20):
                    damageSkill.append((16, time + 1620 + i * 240))
                    damageSkill.append((16, time + 1680 + i * 240))
                    damageSkill.append((16, time + 1740 + i * 240))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000 + 6300)
            elif skillName == '새록새록 꽃누리':
                for i in range(8):
                    damageSkill.append((21, time + 1740 + i * 60))
                for i in range(11):
                    damageSkill.append((22, time + 2220 + i * 60))
                for i in range(5):
                    damageSkill.append((22, time + 3420 + i * 60))
                for i in range(17):
                    damageSkill.append((22, time + 3720 + i * 30))
                for i in range(7):
                    damageSkill.append((22, time + 5940 + i * 60))
                for i in range(24):
                    damageSkill.append((22, time + 6420 + i * 30))
                HekateUntil = max(HekateUntil, time + 5000 + 7110)
            elif skillName == '솔 헤카테 : 스틱스':
                skillRemain[7] -= 1
                if skillRemain[7] < 0:
                    continue # 6회 제한 적용
                damageSkill.append((24, time))
                for i in range(4):
                    damageSkill.append((25, time + 720 + i * 720))
                for i in range(7):
                    damageSkill.append((26, time + 3300 + i * 60))
                HekateSince = max(HekateSince, time + 960)
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '스파이더 인 미러':
                damageSkill.append((17, time))
                for i in range(6):
                    damageSkill.append((18, time + 2700 + i * 8850))
                    damageSkill.append((18, time + 3600 + i * 8850))
                    damageSkill.append((18, time + 4450 + i * 8850))
                    damageSkill.append((18, time + 5200 + i * 8850))
                    damageSkill.append((18, time + 5850 + i * 8850))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '크레스트 오브 더 솔라':
                damageSkill.append((19, time))
                for i in range(24):
                    damageSkill.append((20, time + 2100 + i * 2100))
                if HekateUntil < time and HekateSince < time:
                    HekateSince = time
                HekateUntil = max(HekateUntil, time + 5000)
            elif skillName == '안다미로':
                ascent.append(time / 1000)
        while HekateSince < HekateUntil:
            damageSkill.append((23, HekateSince + 450))
            HekateSince += 3500
        for i in range(15):
            damageSkill.append((1, eruption[0] + 1800 + i * 1800))
        for i in range(10):
            for j in range(4):
                damageSkill.append((2, eruption[1] + 1800 + i * 3000 + 480 + j * 480))
        damageSkill.append((3, eruption[2]))
        for i in range(29):
            damageSkill.append((4, eruption[2] + 2000 + i * 1000))
        for i in range(13):
            damageSkill.append((5, eruption[2] + 2100 + i * 2100 + 750))
        for mountainSeedTurn in range(3):
            for i in range(14):
                damageSkill.append((6, mountainSeed[mountainSeedTurn] + 990 + i * 2000))
        
        damageSkill.sort(key = lambda x: x[1])
        # 화중군자 추가
        Resurrection = [True, False, False, False, False, False,
                  False, False, False, False, False, True,
                  False, True, True, True, True,
                  False, False, False, False,
                  True, True,
                  False, False, False, False, False, False, False]
        ResurrectionSince = 0
        for tl in damageSkill:
            if Resurrection[tl[0]] and ResurrectionSince <= tl[1]:
                damageSkill.append((29, tl[1] + 90))
                damageSkill.append((29, tl[1] + 90))
                damageSkill.append((29, tl[1] + 90))
                damageSkill.append((29, tl[1] + 690))
                damageSkill.append((29, tl[1] + 690))
                damageSkill.append((29, tl[1] + 1290))
                ResurrectionSince = tl[1] + 3760
        damageSkill.sort(key = lambda x: x[1])
        
        damageSkill = list(filter(lambda x: x[1] >= start and x[1] < end, damageSkill))
        
        if PRINTTIMELINE:
            for x in damageSkill:
                wrTL.writerow([skillstr[x[0]], x[1]])
        
        # 일격필살 최적화
        FatalStrike = [True, True, True, True, True, True,
                       False, True, True, True, True, True,
                       True, True, True, True, True,
                       True, False, True, False,
                       True, True,
                       False, False, False, False, False, False, False]

        maxft = 0
        maxscore = 0

        for tl2 in damageSkill:
            FatalTime = ft = tl2[1]
            score = 0
            if FatalTime > 30000:
                break
            for tl in damageSkill:
                if FatalStrike[tl[0]] and tl[1] >= FatalTime:
                    FatalTime = tl[1] + 30000
                Fatal = tl[1] + 30000 > FatalTime and tl[1] + 26000 <= FatalTime
                multiplier = (dR + dRS[tl[0]] + dRA[tl[1]] + Fatal * 100) * (madR + madRA[tl[1]]) * (cdR + cdRA[tl[1]]) * (1 - mobpdpR * mobpdpRS[tl[0]] * mobpdpRA[tl[1]]) * mdRA[tl[1]]
                score += damage[tl[0]] * (multiplier / base_multiplier)
                if score > maxscore:
                    maxscore = score
                    maxft = ft
        for tl2 in damageSkill:
            FatalTime = ft = tl2[1] - 4000
            score = 0
            if FatalTime > 30000:
                break
            for tl in damageSkill:
                if FatalStrike[tl[0]] and tl[1] >= FatalTime:
                    FatalTime = tl[1] + 30000
                Fatal = tl[1] + 30000 > FatalTime and tl[1] + 26000 <= FatalTime
                multiplier = (dR + dRS[tl[0]] + dRA[tl[1]] + Fatal * 100) * (madR + madRA[tl[1]]) * (cdR + cdRA[tl[1]]) * (1 - mobpdpR * mobpdpRS[tl[0]] * mobpdpRA[tl[1]]) * mdRA[tl[1]]
                score += damage[tl[0]] * (multiplier / base_multiplier)
                if score > maxscore:
                    maxscore = score
                    maxft = ft
        maxscore *= 340000 / (end - start)
        print("최종 점수:", int(maxscore), "점")
        print("일격필살 시점:", maxft, "ms")
        res[7] = int(maxscore)
        if end - start > 360000:
            res[8] = False
            print("평가 시간이 6분을 초과했습니다.")
        
        # 실제 계산
        FatalTime = maxft
        partial_score = [0 for x in range(340)]
        partial_addscore = [0 for x in range(340)]
        for tl in damageSkill:
            if FatalStrike[tl[0]] and tl[1] >= FatalTime:
                FatalTime = tl[1] + 30000
            Fatal = tl[1] + 30000 > FatalTime and tl[1] + 26000 <= FatalTime
            multiplier = (dR + dRS[tl[0]] + dRA[tl[1]] + Fatal * 100) * (madR + madRA[tl[1]]) * (cdR + cdRA[tl[1]]) * (1 - mobpdpR * mobpdpRS[tl[0]] * mobpdpRA[tl[1]]) * mdRA[tl[1]]
            slot = int((tl[1] - start) / (end - start) * 340)
            partial_score[slot] += damage[tl[0]] * (multiplier / base_multiplier)
            if (tl[0] == 17):
                partial_addscore[slot] += damage[tl[0]] * 1206 / 2196 * (multiplier / base_multiplier)
            if (tl[0] == 18):
                partial_addscore[slot] += damage[tl[0]] * 469 / 854 * (multiplier / base_multiplier)
            if (tl[0] == 19):
                partial_addscore[slot] += damage[tl[0]] * 2011 / 3661 * (multiplier / base_multiplier)
            if (tl[0] == 20):
                partial_addscore[slot] += damage[tl[0]] * 827 / 1342 * (multiplier / base_multiplier)
            if (tl[0] == 29):
                partial_addscore[slot] += damage[tl[0]] * (multiplier / base_multiplier)
            detail[indetail[tl[0]]] += damage[tl[0]] * (multiplier / base_multiplier)
        if detail[20] < 1:
            res[8] = False
            print("솔 헤카테 : 스틱스가 발동되지 않았습니다.")

        lazy = 0
        for i in range(340):
            partial_score[i] *= 340000 / (end - start)
            partial_addscore[i] *= 340000 / (end - start)
            if partial_score[i] < 1:
                lazy += 1
                if lazy == 10 and res[8]:
                    res[8] = False
                    print("10단위 동안 어떠한 공격도 없었습니다.")
            else:
                lazy = 0
        timepoint = [start / 1000 + x * (end - start) / 340000 for x in range(0, 340)]
        plt.figure(figsize = (10, 6))
        plt.xlim(0, 360)
        for i in range(3):
            plt.axvline(x = ascent[i], color = 'pink', linestyle = 'dashed')
        plt.bar(timepoint, partial_score, width = (end - start) / 340000, color = 'black')
        plt.bar(timepoint, partial_addscore, width = (end - start) / 340000, color = 'green')
        plt.xticks([x * 30 for x in range(13)])
        if PRINTTIMELINE:
            plt.show()
            exportTL.close()
            break
        else:
            plt.savefig('res/' + characterName + '.png')
            plt.cla()   # clear the current axes
            plt.clf()   # clear the current figure
            plt.close() # closes the current figure
        if res[8] == False:
            print("해당 리플레이는 순위에서 제외되었습니다.")

wr.writerow(res)
export.close()
wr2.writerow(detail)
export2.close()
