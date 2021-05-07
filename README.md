# First Order Logic Inference
## CSCI- 561 - Spring 2021 - Foundations of Artificial Intelligence
Homework 3
![Puppies](https://github.com/biyaniM/csci561-hw3-First-Order-Logic-Inference/blob/master/puppy_photo.png)
## Project Description

You have finally found your dream job running an academy for puppies. You are so passionate
about it, you worked long hours and your business is _booming_. There is only one problem: You
have enlisted so many pups into your academy that you are starting to lose track of everything.
Letting a puppy start the academy depends on their vaccination and health status. Even once
they’re in, what they can train for and which other puppies they interact with depends on their
history in the academy. Thankfully, you have a background in AI, so you decide to develop an
automated system that can evaluate all of the information you have and alert you and your
employees whether an action is possible. The system can also provide an instant guideline to
keep owners informed and minimize the risks to these adorable puppies.

You sit down to develop a beta version of the system using **_first-order logic resolution_**. Puppy
status and history data will be encoded as first order logic clauses in the knowledge base. The
knowledge bases contain sentences with the following defined operators:

1.NOT X ~X
2. X OR Y X | Y
3. X AND Y X & Y
4. X IMPLIES Y X => Y

The program takes a query of n actions and provides a logical conclusion to whether each can be
performed or not.

**Format for input.txt:**
```
<N = NUMBER OF QUERIES>
<QUERY 1>
...
<QUERY N>
<K = NUMBER OF GIVEN SENTENCES IN THE KNOWLEDGE BASE>
<SENTENCE 1>
...
<SENTENCE K>
```
The first line contains an integer _N_ specifying the number of queries. The following _N_ lines contain
one query per line. The line after the last query contains an integer _K_ specifying the number of
sentences in the knowledge base. The remaining _K_ lines contain the sentences in the knowledge
base, one sentence per line.


### Query format:
Each query will be a single literal of the form Predicate(Constant_Arguments) or
~Predicate(Constant_Arguments) and will not contain any variables. Each predicate will have
between 1 and 25 constant arguments. Two or more arguments will be separated by commas.

### KB format:
Each sentence in the knowledge base is written in one of the following forms:
1) An _implication_ of the form _p 1_ ∧ _p 2_ ∧ _..._ ∧ _pm_ ⇒ _q,_ where its premise is a conjunction of
literals and its conclusion is a single literal. Remember that a literal is an atomic sentence
or a negated atomic sentence.
2) A single literal: _q_ or ~ _q_

Notes:

1. & denotes the _conjunction_ operator.
2. | denotes the _disjunction_ operator. It will not appear in the queries nor in the KB given as
    input. But you will likely need it to create your proofs.
3. => denotes the _implication_ operator.
4. ~ denotes the _negation_ operator.
5. No other operators besides &, =>, and ~ are used in the knowledge base.
6. There will be no parentheses in the KB except as used to denote arguments of predicates.
7. Variables are denoted by a single lowercase letter.
8. All predicates (such as Vaccinated) and constants (such as Hayley) are case sensitive
    alphabetical strings that begin with uppercase letters.
9. Each predicate takes at least one argument. Predicates will take at most 25 arguments. A
    given predicate name will not appear with different number of arguments.
10. There will be at most 10 queries and 100 sentences in the knowledge base.
11. See the sample input below for spacing patterns.
12. You can assume that the input format is exactly as it is described.
13. There will be no syntax errors in the given input.
14. The KB will be true (i.e., will not contain contradictions).

**Format for output.txt:**

For each query, determine if that query can be inferred from the knowledge base or not, one
query per line:

<ANSWER 1>
...
<ANSWER N>

Each answer should be either TRUE if you can prove that the corresponding query sentence is
true given the knowledge base, or FALSE if you cannot.


### Notes and hints:

- If you decide that the given statement can be inferred from the knowledge base, every
    variable in each sentence used in the proving process should be unified with a Constant
    (i.e., unify variables to constants before you trigger a step of resolution).
- All variables are assumed to be universally quantified. There is no existential quantifier
    in this homework. There is no need for Skolem functions or Skolem constants.
- Operator priorities apply (negation has higher priority than conjunction). There will be
    no parentheses in the sentences, other than around arguments of predicates.
- The knowledge base is consistent.
- If you run into a loop and there is no alternative path you can try, report FALSE. An
    example for this would be having two rules **_(1)_** A(x) => B(x) and **_(2)_** B(x) => A(x) and
    wanting to prove A(Teddy). In this case your program should report FALSE.
- Note that the KB is not in Horn form because we allow more than one positive literal. So
    you indeed must use resolution and cannot use generalized Modus Ponens.

**Example 1:**

For this input.txt:
```
1
Play(Hayley,Teddy)
6
Vaccinated(x) => Start(x)
Start(x) & Healthy(x) => Ready(x)
Ready(x) & Ready(y) => Play(x,y)
Vaccinated(Hayley)
Healthy(Hayley)
Healthy(Teddy)
```
your output.txt should be:
```
FALSE
```

**Example 2:**

For this input.txt:
```
2
Learn(Sit,Ares)
Graduate(Hayley)
8
Ready(x) => Train(Come,x)
Healthy(x) & Train(y,x) => Learn(y,x)
Learn(Come,x) => Train(Sit,x)
Learn(Come,x) & Learn(Sit,x) => Train(Down,x)
Learn(Down,x) => Graduate(x)
Ready(Hayley)
Ready(Ares)
Healthy(Ares)
```
your output.txt should be:
```
TRUE
FALSE
```
**Example 3:**

For this input.txt:
```
3
Play(Ares,Teddy)
Train(Down,Hayley)
Play(Ares,Hayley)
10
Healthy(x) => Ready(x)
Ready(x) => Train(Come,x)
Healthy(x) & Train(y,x) => Learn(y,x)
Learn(Come,x) => Train(Sit,x)
Learn(Come,x) & Learn(Sit,x) => Train(Down,x)
Learn(Down,x) => Graduate(x)
Ready(x) & Ready(y) => Play(x,y)
Healthy(Ares)
Healthy(Hayley)
Learn(Come,Hayley)
```
your output.txt should be:
```
FALSE
TRUE
TRUE
```

**Example 4: (note: a previous typo has been corrected)**

For this input.txt:
```
5
Greet(Hayley,TrainerJosh)
PlayFetch(Luna,TrainerBibek)
ShowOff(Ares,TrainerChristina)
Graduate(Hayley)
Play(Leia,Teddy)
50
Vaccinated(x) => Start(x)
Start(x) & Healthy(x) => Ready(x)
RespondToName(x) => Train(Come,x)
Ready(x) & Train(y,x) => Learn(y,x)
Learn(Come,x) => Train(Sit,x)
Learn(Come,x) & Learn(Sit,x) => Train(Down,x)
Learn(Sit,x) => Train(Paw,x)
Learn(Paw,x) & Working(y) => Greet(x,y)
Scared(x,y) => ~Socialize(x,y)
Ready(x) & Ready(y) & Socialize(x,y) & Socialize(y,x) => Play(x,y)
Learn(Get,x) => Train(Drop,x)
Learn(Come,x) & HoldToy(x) => Train(Get,x)
RespondToName(x) & HoldToy(x) => Train(Drop,x)
Learn(Come,x) & Learn(Get,x) & Learn(Drop,x) => Train(Fetch,x)
Learn(Fetch,x) & Working(y) => PlayFetch(x,y)
Learn(Down,x) => Train(Roll,x)
Learn(Roll,x) & Working(y) => ShowOff(x,y)
RespondToName(x) & Desensitized(Leash,x) => Train(WalkIndoors,x)
Learn(WalkIndoors,x) & Desensitized(Cars,x) => Train(WalkOutdoors,x)
Learn(WalkOutdoors,x) & Learn(Down,x) => Graduate(x)
~Sensitive(y,x) => Desensitized(y,x)
Sensitive(y,x) => TrainDesensitized (y,x)
Sensitive(y,x) & TrainDesensitized(y,x) => Desensitized(y,x)
Vaccinated(Hayley)
Vaccinated(Ares)
~Vaccinated(Leia)
Vaccinated(Luna)
Vaccinated(Teddy)
~Healthy(Ares)
Healthy(Hayley)
Healthy(Luna)
Healthy(Leia)
Healthy(Teddy)
~Scared(Leia,Teddy)
Scared(Teddy,Leia)
~Sensitive(Leash,Hayley)
~Sensitive(Cars,Teddy)
Sensitive(Cars,Luna)
~Sensitive(Cars,Hayley)
Working(TrainerChristina)
~Working(TrainerJosh)
Working(TrainerBibek)
RespondToName(Hayley)
RespondToName(Luna)
RespondToName(Ares)
HoldToy(Luna)
~HoldToy(Leia)
~RespondToName(Leia)
Sensitive(Cars,Leia)
```

your output.txt should be:
```
FALSE
TRUE
FALSE
TRUE
FALSE
```
