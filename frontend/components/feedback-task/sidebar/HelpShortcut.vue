<template>
  <div>
    <p class="shortcuts__title">Shortcuts</p>
    <base-spinner v-if="$fetchState.pending" />
    <documentation-viewer
      v-else
      class="shortcuts__content"
      :content="content"
    />
  </div>
</template>

<script>
export default {
  name: "HelpShortcut",
  data() {
    return {
      content: {
        tabs: [],
      },
    };
  },
  methods: {
    async getShortcutsDocumentation() {
      const folderContent = require.context(
        `../../../../docs/_source/_common/`,
        false,
        /^[^_]+\.md$/,
        "lazy"
      );

      const shortcutContent = await folderContent("./shortcuts.md");
      const shortcuts = shortcutContent.body.split("\n");

      this.removeTitle(shortcuts);

      return this.parseByPlatform(shortcuts);
    },
    removeTitle(shortcuts) {
      shortcuts.shift();
      return shortcuts;
    },
    parseByPlatform(shortcuts) {
      const otherOS = "(Other)";
      const macOsX = "(Mac os)";
      const manipulatedByPlatform = shortcuts
        .map((row) => {
          if (row.includes(otherOS))
            return this.$platform.isMac ? undefined : row.replace(otherOS, "");
          if (row.includes(macOsX))
            return this.$platform.isMac ? row.replace(macOsX, "") : undefined;

          return row;
        })
        .filter(Boolean);

      return manipulatedByPlatform.join("\n");
    },
  },
  async fetch() {
    try {
      this.content.tabs.push({
        id: "shortcuts",
        name: this.$t("shortcuts.label"),
        markdown: await this.getShortcutsDocumentation(),
      });
    } catch (e) {
      console.log(e);
    }
  },
};
</script>

<style lang="scss" scoped>
.shortcuts {
  &__title {
    margin-top: 0;
    margin-bottom: $base-space * 2;
    @include font-size(18px);
    font-weight: 600;
  }
  &__content {
    &.snippet__container {
      width: auto;
    }
  }
}
:deep(.snippet) {
  max-height: calc(100vh - 106px);
  overflow: auto;
}
:deep(table) {
  width: 100%;
  border-collapse: collapse;
  border-radius: $border-radius;
  border-spacing: 0;
  background: palette(grey, 800);
  box-shadow: 0 0.2rem 0.5rem rgba(0, 0, 0, 0.05),
    0 0 0.0625rem rgba(0, 0, 0, 0.1);
  td,
  th {
    display: block;
    border-bottom: 1px solid $black-4;
    border-left: 1px solid $black-4;
    border-right: 1px solid $black-4;
    padding: $base-space;
  }
  th {
    background: $black-4;
    border: none;
  }
  thead tr:last-child th:last-child {
    border-top-right-radius: $border-radius;
  }
  thead tr:first-child th:first-child {
    border-top-left-radius: $border-radius;
  }
  td:last-child,
  th:last-child {
    border-left: none;
    border-right: none;
  }
  td:first-child,
  th:first-child {
    border-left: none;
    border-bottom: none;
  }
  th:last-child {
    display: none;
  }
  code {
    padding: calc($base-space / 2);
    border: 1px solid $black-10;
    border-radius: $border-radius;
    background: $black-4;
  }
}
</style>
