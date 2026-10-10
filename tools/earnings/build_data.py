"""Build static/data/earnings.json from the NYT / HEA Group major-earnings workbook.

Usage:
    python3 tools/earnings/build_data.py path/to/NYT_HEA_Major_Earnings.xlsx

Chinese names live in schools_zh.tsv (keyed by OPEID6) and majors_zh.tsv
(keyed by CIP4). The script fails if any school or major is missing a
Chinese name, so new rows in a future workbook must be translated first.
"""
import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'static', 'data', 'earnings.json')

# The workbook truncates a few CIP titles; use the full NCES names instead.
MAJOR_NAME_FIXES = {
    '1401': 'Engineering, General',
    '1511': 'Engineering-Related Technologies/Technicians',
}

# Common abbreviations parents search for (matched in addition to the names).
SCHOOL_ALIASES = {
    '1315': 'UCLA', '1312': 'UC Berkeley Cal', '1317': 'UCSD', '1313': 'UC Davis',
    '1314': 'UCI UC Irvine', '1320': 'UCSB', '1321': 'UCSC', '1316': 'UCR',
    '41271': 'UC Merced', '2178': 'MIT', '2785': 'NYU', '1328': 'USC',
    '1775': 'UIUC', '1776': 'UIC', '3242': 'CMU', '3378': 'UPenn Penn Wharton',
    '1131': 'Caltech', '3754': 'Virginia Tech VT', '1569': 'Georgia Tech GT',
    '2325': 'UMich', '3895': 'UW Madison', '3798': 'UW UDub', '3658': 'UT Austin',
    '2103': 'UMD', '2974': 'UNC', '3329': 'Penn State PSU', '3090': 'OSU',
    '2803': 'RPI', '2806': 'RIT', '2233': 'WPI', '2629': 'Rutgers',
    '2838': 'SBU', '2837': 'UB', '2836': 'Binghamton', '2707': 'Columbia',
    '3024': 'CWRU', '2520': 'WashU WUSTL', '2077': 'JHU', '3705': 'W&M',
    '3745': 'UVA', '3768': 'W&L', '1143': 'Cal Poly SLO', '1144': 'Cal Poly Pomona',
    '1151': 'SDSU', '1154': 'SFSU', '1153': 'CSUN', '1139': 'CSULB',
    '1137': 'CSUF', '3632': 'TAMU', '3644': 'TTU', '9741': 'UTD',
    '3954': 'UCF', '1537': 'USF', '9635': 'FIU', '1489': 'FSU',
    '1535': 'UF', '1598': 'UGA', '3969': 'UMN', '2221': 'UMass',
    '2199': 'NEU', '2130': 'BU', '2128': 'BC', '1739': 'NU',
    '1774': 'UChicago', '2711': 'Cornell', '2155': 'Harvard', '1426': 'Yale',
    '2627': 'Princeton', '3401': 'Brown', '2573': 'Dartmouth', '1305': 'Stanford',
    '2920': 'Duke', '3604': 'Rice', '3535': 'Vanderbilt', '1840': 'Notre Dame ND',
    '1564': 'Emory', '1445': 'Georgetown', '1444': 'GWU', '1434': 'AU',
    '2219': 'Tufts', '2133': 'Brandeis', '2894': 'UR', '3256': 'Drexel',
    '3371': 'Temple', '3379': 'Pitt', '1809': 'IU', '1825': 'Purdue',
    '1869': 'ISU', '1892': 'UIowa', '2290': 'MSU', '1083': 'UA UArizona',
    '1081': 'ASU', '3675': 'UofU', '1370': 'CU Boulder', '3223': 'UO',
    '3210': 'OSU Oregon State', '3800': 'WSU', '1417': 'UConn', '1431': 'UD',
    '2866': 'FIT', '2798': 'Pratt', '3409': 'RISD', '21415': 'SCAD',
    '1753': 'SAIC', '2742': 'Juilliard', '2126': 'Berklee', '2710': 'Cooper Union',
    '20662': 'Parsons', '1479': 'ERAU', '1691': 'IIT', '2621': 'NJIT',
    '2639': 'Stevens', '1830': 'Rose-Hulman', '39463': 'Olin', '1348': 'Mines',
    '2517': 'Missouri S&T', '2292': 'MTU', '3868': 'MSOE', '11644': 'UMGC',
}


def main(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    rows = list(wb['All Programs'].iter_rows(values_only=True))
    header, rows = rows[0], rows[1:]
    col = {name: i for i, name in enumerate(header)}

    school_zh = load_tsv('schools_zh.tsv')
    major_zh = load_tsv('majors_zh.tsv')

    schools, school_idx = [], {}
    majors, major_idx = [], {}
    programs = []
    missing = set()

    for r in rows:
        opeid, cip = str(r[col['OPEID6']]), str(r[col['CIP4']])
        if opeid not in school_idx:
            if opeid not in school_zh:
                missing.add(('school', opeid, r[col['Institution']]))
            school_idx[opeid] = len(schools)
            schools.append([
                r[col['Institution']].strip(),
                school_zh.get(opeid, ''),
                r[col['State']],
                SCHOOL_ALIASES.get(opeid, ''),
                opeid,
            ])
        if cip not in major_idx:
            if cip not in major_zh:
                missing.add(('major', cip, r[col['Major']]))
            major_idx[cip] = len(majors)
            majors.append([
                MAJOR_NAME_FIXES.get(cip, r[col['Major']].strip()),
                major_zh.get(cip, ''),
                cip,
            ])
        net = r[col['Net Price']]
        programs.append([
            school_idx[opeid],
            major_idx[cip],
            r[col['Median Earnings 4 Yrs After Completion']],
            r[col['Earnings Benchmark (HS Median)']],
            1 if r[col['Pass/Fail']] == 'Pass' else 0,
            r[col['# Completers in Earnings Cohort']],
            net if isinstance(net, (int, float)) else None,
        ])

    if missing:
        for kind, key, name in sorted(missing):
            print(f'missing Chinese name for {kind} {key}: {name}', file=sys.stderr)
        sys.exit(1)

    programs.sort(key=lambda p: -p[2])
    data = {
        'fields': {
            'schools': ['name', 'nameZh', 'state', 'aliases', 'opeid6'],
            'majors': ['name', 'nameZh', 'cip4'],
            'programs': ['school', 'major', 'medianEarnings', 'hsBenchmark',
                         'passesBenchmark', 'cohortSize', 'netPrice'],
        },
        'schools': schools,
        'majors': majors,
        'programs': programs,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f'wrote {len(programs)} programs, {len(schools)} schools, '
          f'{len(majors)} majors to {os.path.normpath(OUT)}')


def load_tsv(name):
    out = {}
    with open(os.path.join(HERE, name), encoding='utf-8') as f:
        for line in f:
            if line.strip():
                key, value = line.rstrip('\n').split('\t')
                out[key] = value
    return out


if __name__ == '__main__':
    main(sys.argv[1])
