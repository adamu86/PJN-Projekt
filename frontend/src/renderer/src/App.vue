<script setup lang="ts">
import Button from 'primevue/button';
import TextInput from 'primevue/inputtext';
import { onMounted, onUpdated, ref } from 'vue';
import Fieldset from 'primevue/fieldset';
import Textarea from 'primevue/textarea';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';

const question = ref<string>('');
const answer = ref<string>('');
const history = ref<{question: string, answer: string}[]>([]);

const getAnswer = async () => {
  const res = await window.electron.ipcRenderer.invoke('ask', question.value);

  const objects = res.map(([text, score]) => ({ text, score }));

  answer.value = objects.map((item) => item.text).join("\n\n");

  history.value.unshift({ question: question.value, answer: answer.value });
}
</script>

<template>
  <div>
    <Tabs value="0">
      <TabList>
        <Tab value="0">Zadaj pytanie</Tab>
        <Tab value="1">Historia</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <div class="grid gap-5 grid-rows-[auto_1fr] h-full">
            <Fieldset legend="Zadaj pytanie" class="w-full h-min rounded-xl!">
              <div class="flex gap-5">
                <TextInput v-model="question" placeholder="Twoje pytanie..." class="w-full"/>
                <Button label="Zatwierdź" @click="getAnswer"></Button>
              </div>
            </Fieldset>
            <Fieldset legend="Odpowiedź" class="w-full [&_div]:h-100 rounded-xl!">
              <Textarea v-model="answer" readonly fluid placeholder="Tu pojawi się odpowiedź..." class="resize-none cursor-default h-full"/>
            </Fieldset>
          </div>
        </TabPanel>
        <TabPanel value="1">
          
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>
