export interface Answer {
  answer: string
  sentence: string
  passage: string
}

export const defaultAnswer: Answer = {
  answer: '',
  sentence: '',
  passage: ''
}

export interface QuestionAnswer {
    question: string;
    answer: Answer
}