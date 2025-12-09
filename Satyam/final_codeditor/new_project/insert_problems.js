db.coding_problems.deleteMany({});
db.coding_problems.insertMany([
  {
    "id": "1",
    "title": "Sum Two Numbers",
    "description": "Write a program that takes two numbers and returns their sum.",
    "difficulty": "Easy",
    "labels": ["arithmetic", "basic", "beginner"],
    "sample_input": "3 5",
    "sample_output": "8",
    "constraints": "1 <= a, b <= 1000"
  },
  {
    "id": "2",
    "title": "Prime Number Checker",
    "description": "Check if a given number is prime.",
    "difficulty": "Medium",
    "labels": ["math", "number-theory"],
    "sample_input": "7",
    "sample_output": "Yes",
    "constraints": "1 <= n <= 10000"
  },
  {
    "id": "3",
    "title": "Array Sum",
    "description": "Find the sum of all elements in an array.",
    "difficulty": "Easy",
    "labels": ["arrays", "loops"],
    "sample_input": "3 1 2 3",
    "sample_output": "6",
    "constraints": "1 <= n <= 100"
  }
]);
db.coding_problems.find().pretty();
