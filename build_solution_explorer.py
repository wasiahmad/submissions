import glob
import json
from datetime import datetime

import pandas as pd

from lcb_runner.lm_styles import LanguageModelList

problems = []

all_outputs = {}


def get_url(jsonrow):
    if jsonrow["platform"] == "leetcode":
        return f"https://leetcode.com/problems/{jsonrow['question_title']}"
    if jsonrow["platform"] == "atcoder":
        return f"https://atcoder.jp/contests/{jsonrow['contest_id']}/tasks/{jsonrow['question_id']}"
    if jsonrow["platform"] == "codeforces":
        return f"https://codeforces.com/problemset/problem/{jsonrow['contest_id']}/{jsonrow['question_id'].split('_')[1]}"


for idx, model in enumerate(LanguageModelList):

    fnames = [
        f"{model.model_repr}/Scenario.codegeneration_*_eval_all.json"
        # for i in range(9)
    ]
    fname = sum([glob.glob(fname) for fname in fnames], [])

    if not fname:
        print(fnames, "not found")
        # print(f"{fname} does not exist")
        fname = f".json"
        fname = glob.glob(fname)
        if not fname:
            # print(f"{fname} does not exist")
            continue
        else:
            assert len(fname) == 1
        fname = fname[0]
    else:
        fname = [
            f for f in fname if "_200" not in f and "_125" not in f and "_150" not in f
        ]
        assert len(fname) == 1, fname
        fname = fname[0]

    checked_samples_file = fname

    model_name = checked_samples_file.split("/")[-2]
    with open(checked_samples_file, "r") as f:
        checked_samples = json.load(f)
        checked_samples = sorted(checked_samples, key=lambda x: str(x["question_id"]))

    if len(checked_samples) != 880:
        continue

    if not problems:
        for k in checked_samples:
            problems.append(
                {
                    "question_id": k["question_id"],
                    "question_title": k["question_title"],
                    "question_content": k["question_content"],
                    "contest_date": k["contest_date"],
                    "difficulty": k["difficulty"],
                    "url": get_url(k),
                }
            )

    all_outputs[model_name] = []
    for k in checked_samples:
        all_outputs[model_name].append(
            {
                "code_list": k["code_list"],
                "pass1_list": k["graded_list"],
                "metadata_list": k["metadata"] if "metadata" in k else [],
            }
        )

    assert len(checked_samples) == len(
        problems
    ), f"{len(checked_samples)=} != {len(problems)=} for {model_name=}"

with open("../../code_generation_samples/problems.json", "w") as f:
    json.dump(problems, f, indent=4)

with open("../../code_generation_samples/all_outputs.json", "w") as f:
    json.dump(all_outputs, f, indent=4)
