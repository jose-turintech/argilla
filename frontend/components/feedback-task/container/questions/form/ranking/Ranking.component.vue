<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />
    <DndSelectionComponent
      :ranking="ranking"
      @on-reorder="onChanged"
      :isFocused="isFocused"
      @on-focus="onFocus"
    />
  </div>
</template>

<script>
import { adaptQuestionsToSlots } from "./ranking-adapter";

export default {
  name: "RankingComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
    showSuggestion: {
      type: Boolean,
      default: () => false,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  computed: {
    options() {
      return this.question.answer.values;
    },
    ranking() {
      return adaptQuestionsToSlots({ options: this.options });
    },
  },
  methods: {
    onChanged(newQuestionRanked) {
      this.options.forEach((option) => {
        option.rank = newQuestionRanked.getRanking(option);
      });
    },
    onFocus() {
      this.$emit("on-focus");
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
</style>
