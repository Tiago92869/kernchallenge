export function getApiErrorMessage(error, fallbackMessage = 'Something went wrong. Please try again.') {
  const apiMessage = error?.response?.data?.error?.message
  if (typeof apiMessage === 'string' && apiMessage.trim()) {
    return apiMessage
  }

  const networkMessage = error?.message
  if (typeof networkMessage === 'string' && networkMessage.trim()) {
    return networkMessage
  }

  return fallbackMessage
}
