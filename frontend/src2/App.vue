<template>
	<div class="flex h-screen w-screen overflow-hidden bg-white text-base antialiased">
		<div v-if="!hideSidebar" class="h-full border-r bg-gray-50">
			<AppSidebar />
		</div>

		<div class="flex h-full flex-1 flex-col overflow-auto">
			<Suspense>
				<RouterView />
			</Suspense>
		</div>

		<template v-if="!isGuestView">
			<component v-for="dialog in dialogs" :is="dialog" :key="dialog.id" />
		</template>

		<Toaster
			position="bottom-right"
			:expand="true"
			:close-button="true"
			:toast-options="{ duration: 4000 }"
		/>
	</div>
</template>

<script setup lang="ts">
import { Socket } from 'socket.io-client'
import { computed, inject, onBeforeUnmount, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { Toaster } from 'vue-sonner'
import AppSidebar from './components/AppSidebar.vue'
import { dialogs } from './helpers/confirm_dialog'
import { waitUntil } from './helpers/index.ts'
import { createToast } from './helpers/toasts.ts'
import session from './session'
import telemetry from './telemetry.ts'

const route = useRoute()
const hideSidebar = ref(true)
watchEffect(() => {
	if (route.fullPath === '/') return
	hideSidebar.value = Boolean(route.meta.isGuestView || route.meta.hideSidebar)
})

const isGuestView = computed(() => route.meta.isGuestView || !session.isLoggedIn)
waitUntil(() => session.isLoggedIn).then(() => {
	telemetry.init()
})

const $socket = inject<Socket>('$socket')!
$socket.on('insights_notification', (data: any) => {
	if (data.user == session.user.email) {
		createToast({
			title: data.title || data.message,
			message: data.title ? data.message : '',
			variant: data.type,
		})
	}
})
onBeforeUnmount(() => {
	$socket.off('insights_notification')
})
</script>
