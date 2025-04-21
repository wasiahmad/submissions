import glob
import json
from datetime import datetime

import pandas as pd

from lcb_runner.lm_styles import LanguageModelList


def load_performances_generation():
    results = []
    for model in LanguageModelList:
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
            assert len(fname) == 1, fname
            fname = fname[0]

        with open(fname) as fp:
            model_outputs = json.load(fp)
        if len(model_outputs) != 1055:
            continue
        assert (
            model.release_date is not None
        ), f"Model {model.model_repr} has no release date"

        results.extend(
            [
                {
                    # "model_class": model,
                    "question_id": model_output["question_id"],
                    "model": model.model_repr,
                    "date": datetime.fromisoformat(model_output["contest_date"]),
                    "difficulty": model_output["difficulty"],
                    "pass@1": (
                        model_output["pass1"] * 100
                        if "pass1" in model_output
                        else model_output["pass@1"] * 100
                    ),
                    "platform": (
                        "leetcode"
                        if isinstance(model_output["question_id"], int)
                        else (
                            "codeforces"
                            if model_output["question_id"][0] == "1"
                            else model_output["platform"]
                        )
                    ),
                }
                for model_output in model_outputs
            ]
        )

    df = pd.DataFrame(results)
    # print(df.head())
    return df


if __name__ == "__main__":
    date_marks = (
        [datetime(2023, m, 1) for m in range(5, 13)]
        + [datetime(2024, m, 1) for m in range(1, 13)]
        + [datetime(2025, m, 1) for m in range(1, 6)]
    )

    date_marks = [int(d.timestamp() * 1000) for d in date_marks]

    df = load_performances_generation()

    # list of dictified rows
    performances = df.to_dict(orient="records")
    for p in performances:
        p["date"] = int(p["date"].timestamp() * 1000) + 1000 * 60 * 60 * 24

    considered_models = set(df["model"])
    model_list = [
        model.to_dict()
        for model in LanguageModelList
        if model.model_repr in considered_models
    ]

    with open("performances_generation.json", "w") as f:
        json.dump(
            {
                "performances": performances,
                "models": model_list,
                "date_marks": date_marks,
            },
            f,
            indent=4,
        )
