<script setup lang="ts">
import Button from 'primevue/button';
import TextInput from 'primevue/inputtext';
import { onMounted, ref } from 'vue';
import Fieldset from 'primevue/fieldset';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import Accordion from 'primevue/accordion';
import AccordionPanel from 'primevue/accordionpanel';
import AccordionHeader from 'primevue/accordionheader';
import AccordionContent from 'primevue/accordioncontent';
import ScrollPanel from 'primevue/scrollpanel';

const question = ref<string>('');
const answer = ref<string>('');
const history = ref<{question: string, answer: string}[]>([]);

const save = async () => {
  window.electron.ipcRenderer.invoke(
    'save', 
    history.value.map(item => ({
      question: item.question,
      answer: item.answer
    }))
  );
}

const getAnswer = async () => {
  if (question.value.length > 0) {
    const res = await window.electron.ipcRenderer.invoke('ask', question.value);

    const objects = res.map(([text, score]) => ({ text, score }));

    answer.value = objects.map((item) => item.text).join("\n\n");

    history.value.unshift({ question: question.value, answer: answer.value });

    save();
  }
}

const deleteAnswer = (index: number) => {
  history.value.splice(index, 1);

  save();
}

onMounted(async () => {
  const res = await window.electron.ipcRenderer.invoke('load');

  history.value = res;
});
</script>

<template>
  <Tabs value="0">
    <TabList class="sticky top-0 z-10 bg-white">
      <Tab value="0">Zadaj pytanie</Tab>
      <Tab value="1">Historia pytań</Tab>
    </TabList>
    <TabPanels>
      <TabPanel value="0">
        <div class="grid gap-5 grid-rows-[auto_1fr] h-full">
          <Fieldset legend="Zadaj pytanie" class="w-full h-min rounded-xl!">
            <div class="flex gap-5">
              <TextInput v-model="question" placeholder="Twoje pytanie..." class="w-full"/>
              <Button color="primary" label="Zatwierdź" @click="getAnswer"></Button>
            </div>
          </Fieldset>
          <Fieldset legend="Odpowiedź" class="w-full [&_div]:h-100 rounded-xl!">
            <ScrollPanel style="width: 100%; height: 100%">
              <p class="whitespace-pre-line mr-5">
                {{ answer ?? 'Tu pojawi się odpowiedź...' }}
              </p>
            </ScrollPanel>
          </Fieldset>
        </div>
      </TabPanel>
      <ScrollPanel style="width: 100%; height: calc(100vh - 6rem)">
        <TabPanel value="1" class="overflow-y-hidden! mr-5">
          <Accordion v-if="history.length > 0" value="0">
            <AccordionPanel v-for="({ question, answer }, index) in history" :key="index" :value="index">
              <AccordionHeader>
                <h1>
                  {{ question }}
                </h1>
              </AccordionHeader>
              <AccordionContent>
                <ScrollPanel style="width: 100%; height: 350px">
                  <div class="m-0 whitespace-pre-line flex flex-col gap-4.5 mr-6">
                    <p class="bg-white/5 p-5 rounded-lg">
                      {{ answer }}
                    </p>
                    <Button class="ml-auto" severity="danger" label="Usuń z historii" @click="deleteAnswer(index)"></Button>
                  </div>
                </ScrollPanel>
              </AccordionContent>
            </AccordionPanel>
          </Accordion>
          <p v-else class="text-center text-gray-400 mt-10 h-full italic">
            Tu pojawi się historia pytań...
          </p>
        </TabPanel>
      </ScrollPanel>
    </TabPanels>
  </Tabs>
</template>
