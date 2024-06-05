<template>
   <router-view></router-view>
</template>

<script>
export default {
  name: 'App',
  rtl: true,
  data: () => ({
      tab: null,
    }),
  methods: {
    
    },
  }
</script>

<style>
*
{
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  font-family: 'Open Sans';
  letter-spacing: normal;
}

body, html
{
  height: 100dvh;
  background-color: #fafafa;
  overflow: visible;
  color: #333;
}

.v-input--density-custom-text-input-density .v-field--variant-outlined, .v-input--density-custom-text-input-density .v-field__input {
  height: 40px;
  padding-top: 0px;
  padding-bottom: 0px;
}

.v-input--custom-text-input-density .v-field--variant-outlined, .v-input--custom-text-input-density .v-field--single-line, .v-input--custom-text-input-density .v-field--no-label {
  padding-bottom: 7px;
}

.v-input--density-custom-text-input-density .v-field--variant-solo, .v-input--custom-text-input-density .v-field--variant-solo-inverted, .v-input--custom-text-input-density .v-field--variant-solo-filled, .v-input--custom-text-input-density .v-field--variant-filled {
  --v-input-control-height: 48px;
  --v-field-padding-bottom: 0px;
}

.v-input--custom-text-input-density .v-field--variant-solo .v-label.v-field-label--floating, .v-input--custom-text-input-density .v-field--variant-solo-inverted .v-label.v-field-label--floating, .v-input--custom-text-input-density .v-field--variant-filled .v-label.v-field-label--floating, .v-input--custom-text-input-density .v-field--variant-solo-filled .v-label.v-field-label--floating {
  top: 2.5px;
}
.v-input--custom-text-input-density .v-field__input {
  row-gap: 3.5px;
}

.ff-card
{
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  border: 1px solid #7f7f7f;
  background-color: #ffffff;
  font-size: 14px;
}

.ff-card-property
{
  font-weight: bold;
}

.ff-card-property span
{
  font-weight: normal;
}

.v-ripple__container
{
  opacity: 0.25;
}

.v-btn__overlay
{
  display: none;
}

.v-btn:focus-visible::after
{
  border: none;
}

.ff-btn
{
  height: 40px !important;
  font-size: 18px !important;
  font-weight: 500;
  color: #fafafa !important;
  background-color: #d10019 !important;
  transition: unset !important;
  padding: 0px 8px;
}

.ff-btn .v-btn__prepend
{
  margin-left: 4px;
  margin-right: -4px;
}

.ff-outlined-btn
{
  height: 40px !important;
  font-size: 18px !important;
  font-weight: 500;
  color: #d10019 !important;
  border: 2px solid #d10019 !important;
  background-color: transparent;
  transition: unset !important;
  padding: 0px 8px;
}

.ff-outlined-btn:hover
{
  background-color: #7c00000a !important;
  color: #7c0000 !important;
  border: 2px solid #7c0000 !important;
  transition: unset !important;
}

.ff-btn:hover, .ff-main-button:hover
{
  background-color: #7c0000 !important;
  transition: unset !important;
}

.ff-main-button
{
  display: flex;
  flex-wrap: wrap;
  flex-direction: column !important;
  width: 100%;
  max-width: 400px;
  align-self: center;
  height: 110px !important;
  font-size: 18px !important;
  font-weight: 500;
  padding: 4px;
  color: #fafafa !important;
  background-color: #d10019 !important;
  transition: unset !important;
}

.ff-main-button .v-btn__prepend
{
  margin: 0;
  font-size: 50px;
  margin-bottom: 4px;
}

.main-section
{
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  align-items: center;
  min-height: 100dvh;
}

.contents-row
{
  display: flex;
  padding-top: 50px;
  padding-bottom: 30px;
  flex-wrap: wrap;
  flex-direction: column;
  width: 100%;
  max-width: 900px;
}

.error-details
{
  min-height: 20px;
  line-height: 20px;
}

#app 
{
  min-height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  justify-content: center;
  color: #333;
}
</style>
