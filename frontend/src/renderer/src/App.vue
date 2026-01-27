<script setup lang="ts">
import Button from 'primevue/button';
import TextInput from 'primevue/inputtext';
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
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Tag from 'primevue/tag';
import { onMounted, reactive, ref, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { Answer, QuestionAnswer, defaultAnswer } from './answer';
import { closeApp, minimizeApp, showError, showSuccess } from './utils';

const toast = useToast();

const question = ref<string>('');
let answer = reactive<Answer>({ ...defaultAnswer });
const history = ref<QuestionAnswer[]>([]);

const getAnswer = async () => {
  if (question.value.length > 0) {
    const res: Answer = await window.electron.ipcRenderer.invoke('ask', question.value);
    Object.assign(answer, res);
    history.value.unshift({ question: question.value, answer: { ...answer } })
    showSuccess(toast);
  } else {
    showError(toast);
  }
}

const saveAnswers = async () => {
  await window.electron.ipcRenderer.invoke(
    'save',
    history.value.map((item: QuestionAnswer) => ({
      question: item.question,
      answer: { ...item.answer }
    }))
  );
}

const clearAnswer = () => {
  question.value = '';
  Object.assign(answer, { ...defaultAnswer });
}

const deleteAnswer = (index: number) => {
  history.value.splice(index, 1);
}

watch(history, () => {
  saveAnswers();
}, { deep: true })

onMounted(async () => {
  history.value = await window.electron.ipcRenderer.invoke('load');;
});
</script>

<template>
  <Toast position="top-center" class="w-54! **:my-auto!"></Toast>
  <Toolbar class="titlebar p-1!">
    <template #start class="flex">
      <!-- <img src="./assets/pb.webp" class="h-5 ml-2"> -->
      <span class="ml-2">Q&A</span>
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
        <span>Zadaj pytanie</span>
      </Tab>
      <Tab value="1" class="flex gap-2!">
        <div class="pi pi-history my-auto"></div>
        <span>Historia pytań</span>
      </Tab>
    </TabList>
    <TabPanels>
      <TabPanel value="0">
        <div class="grid gap-5 grid-rows-[auto_1fr] h-full">
          <Fieldset legend="Zadaj pytanie" class="w-full h-min rounded-xl!">
            <div class="flex gap-5">
              <IconField class="w-full">
                <TextInput v-model="question" @keydown.enter="getAnswer" placeholder="Twoje pytanie..." class="w-full"></TextInput>
                <InputIcon class="pi pi-times cursor-pointer" @click="clearAnswer"></InputIcon>
              </IconField>
              <Button icon="pi pi-check" class="px-5!" color="primary" label="Zatwierdź" @click="getAnswer"></Button>
            </div>
          </Fieldset>
          <Fieldset legend="Wynik" class="w-full [&_div]:h-100 rounded-xl!">
            <ScrollPanel style="width: 100%; height: 100%">
              <Transition name="fade" mode="out-in">
                <article v-if="answer.answer.length > 0" :key="answer.answer" class="whitespace-pre-line mr-4 text-justify grid gap-2">
                  <Tag class="p-2.5! w-min bg-black!" style="border: 1px solid; border-color: rgb(255,255,255,.25);">Odpowiedź</Tag>
                  <span class="mb">{{ answer.answer }}</span>
                  <Tag class="p-2.5! w-min bg-black! mt-4" style="border: 1px solid; border-color: rgb(255,255,255,.25);">Kontekst</Tag>
                  <span>{{ answer.passage }}</span>
                </article>
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
          <Accordion v-if="history.length > 0" value="0" class="mr-6 border border-white/15 rounded-lg">
            <AccordionPanel v-for="({ question, answer }, index) in history" :key="index" :value="index">
              <AccordionHeader>
                <h1>{{ question }}</h1>
              </AccordionHeader>
              <AccordionContent>
                <ScrollPanel style="width: 100%; max-height: 500px">
                  <div class="m-0 whitespace-pre-line grid gap-4 mr-6">
                    <p class="bg-white/2.5 border-white/15 border p-4 rounded-lg text-justify whitespace-pre-line grid gap-2">
                      <Tag class="p-2.5! w-min bg-black!" style="border: 1px solid; border-color: rgb(255,255,255,.25);">Odpowiedź</Tag>
                      <span class="mb">{{ answer.answer }}</span>
                      <Tag class="p-2.5! w-min bg-black! mt-4" style="border: 1px solid; border-color: rgb(255,255,255,.25);">Kontekst</Tag>
                      <span>{{ answer.passage }}</span>
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