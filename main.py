

def main():
    print("Hello from llm-research-bench!")
    from datasets import load_dataset

    ds = load_dataset("hotpotqa/hotpot_qa", "distractor")
    print(ds)                 # shows splits
    example = ds["train"][0]
    for context in example["context"]["sentences"]:
        print(context)



if __name__ == "__main__":
    main()
