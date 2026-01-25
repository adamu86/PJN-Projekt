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
import Toolbar from 'primevue/toolbar';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';

const toast = useToast();

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

    showSuccess();
  } else {
    showError();
  }
}

const deleteAnswer = (index: number) => {
  history.value.splice(index, 1);

  save();
}

const closeApp = () => {
  window.electron.ipcRenderer.send('close')
}

const minimizeApp = () => {
  window.electron.ipcRenderer.send('minimize')
}

const showSuccess = () => {
    toast.add({ severity: 'success', summary: 'Sukces', life: 1500 });
};

const showError = () => {
    toast.add({ severity: 'error', summary: 'Wpisz pytanie', life: 1500 });
};

onMounted(async () => {
  const res = await window.electron.ipcRenderer.invoke('load');

  history.value = res;
});
</script>

<template>
  <Toast position="top-center" class="w-54! **:my-auto!"></Toast>
  <Toolbar class="titlebar p-1!">
    <template #start class="flex">
      <img src="./assets/pb.webp" class="h-5 mx-2">
      <span>Q&A</span>
    </template>
    <template #end>
      <Button icon="pi pi-minus" severity="info" size="small" @click="minimizeApp" text/>
      <Button icon="pi pi-times" severity="danger" size="small" @click="closeApp" text/>
    </template>
  </Toolbar>
  <Tabs value="0">
    <TabList>
      <Tab value="0" class="flex gap-2!">
        <div class="pi pi-question my-auto"></div>
        <span>
          Zadaj pytanie
        </span>
      </Tab>
      <Tab value="1" class="flex gap-2!">
        <div class="pi pi-history my-auto"></div>
        <span>
          Historia pytań
        </span>
      </Tab>
    </TabList>
    <TabPanels>
      <TabPanel value="0">
        <div class="grid gap-5 grid-rows-[auto_1fr] h-full">
          <Fieldset legend="Zadaj pytanie" class="w-full h-min rounded-xl!">
            <div class="flex gap-5">
              <IconField class="w-full">
                <TextInput v-model="question" @keydown.enter="getAnswer" placeholder="Twoje pytanie..." class="w-full"></TextInput>
                <InputIcon class="pi pi-times cursor-pointer" @click="question = ''; answer = ''"></InputIcon>
              </IconField>
              <Button icon="pi pi-check" class="px-5!" color="primary" label="Zatwierdź" @click="getAnswer"></Button>
            </div>
          </Fieldset>
          <Fieldset legend="Odpowiedź" class="w-full [&_div]:h-100 rounded-xl!">
            <ScrollPanel style="width: 100%; height: 100%">
              <Transition name="fade" mode="out-in">
                <p v-if="answer.length > 0" :key="answer" class="whitespace-pre-line mr-5">
                  {{ answer }}
                </p>
                <p v-else class="text-center text-gray-600 pt-4 h-full italic">
                  Tu pojawi się odpowiedź...
                </p>
              </Transition>
            </ScrollPanel>
          </Fieldset>
        </div>
      </TabPanel>
      <TabPanel value="1">
        <ScrollPanel style="width: 100%; height: calc(100vh - 6rem)">
          <Accordion v-if="history.length > 0" value="0" class="mr-6">
            <AccordionPanel v-for="({ question, answer }, index) in history" :key="index" :value="index">
              <AccordionHeader>
                <h1>
                  <span>
                    {{ question }}
                  </span>
                </h1>
              </AccordionHeader>
              <AccordionContent>
                <ScrollPanel style="width: 100%; height: 350px">
                  <div class="m-0 whitespace-pre-line flex flex-col gap-4.5 mr-6">
                    <p class="bg-white/5 p-5 rounded-lg">
                      {{ answer }}
                    </p>
                    <Button icon="pi pi-trash" class="ml-auto" severity="danger" label="Usuń z historii" @click="deleteAnswer(index)"></Button>
                  </div>
                </ScrollPanel>
              </AccordionContent>
            </AccordionPanel>
          </Accordion>
          <p v-else class="text-center text-gray-600 pt-4 h-full italic">
            Tu pojawi się historia pytań...
          </p>
        </ScrollPanel>
      </TabPanel>
    </TabPanels>
  </Tabs>
</template>
